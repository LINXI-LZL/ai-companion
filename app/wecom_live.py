import base64
import binascii
import hashlib
import hmac
import os
import struct
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs


CONFIG_FIELDS = (
    "WECOM_CORP_ID",
    "WECOM_KF_SECRET",
    "WECOM_KF_TOKEN",
    "WECOM_KF_ENCODING_AES_KEY",
    "WECOM_OPEN_KFID",
)

CALLBACK_FIELDS = (
    "WECOM_CORP_ID",
    "WECOM_KF_TOKEN",
    "WECOM_KF_ENCODING_AES_KEY",
)

OPTIONAL_FIELDS = ("WECOM_CALLBACK_PUBLIC_URL",)
SEND_FIELDS = ("WECOM_CORP_ID", "WECOM_KF_SECRET", "WECOM_OPEN_KFID")
AES_BLOCK_SIZE = 16
WECOM_PAD_BLOCK_SIZE = 32


class WeComCryptoError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class WeComLiveConfig:
    def __init__(self, values):
        self.values = {field: (values.get(field) or "").strip() for field in (*CONFIG_FIELDS, *OPTIONAL_FIELDS)}

    @property
    def token(self):
        return self.values["WECOM_KF_TOKEN"]

    @property
    def open_kfid(self):
        return self.values["WECOM_OPEN_KFID"]

    @property
    def missing_fields(self):
        return [field for field in CONFIG_FIELDS if not self.values[field]]

    @property
    def callback_missing_fields(self):
        return [field for field in CALLBACK_FIELDS if not self.values[field]]

    @property
    def configured(self):
        return len(self.missing_fields) == 0

    @property
    def callback_configured(self):
        return len(self.callback_missing_fields) == 0

    @property
    def send_configured(self):
        return all(self.values[field] for field in SEND_FIELDS)

    def to_status(self):
        key_status = validate_encoding_aes_key(self.values["WECOM_KF_ENCODING_AES_KEY"])
        crypto_ready = self.callback_configured and key_status == "ok"
        crypto_status = "ready" if crypto_ready else ("key_ready" if key_status == "ok" else key_status)
        return {
            "channel": "wecom_live",
            "configured": self.configured,
            "callback_configured": self.callback_configured,
            "callback_missing_fields": self.callback_missing_fields,
            "ready_for_real_callback": crypto_ready,
            "crypto_status": crypto_status,
            "send_mode": "real_text_send" if self.send_configured else "payload_only",
            "public_callback_url": self.values["WECOM_CALLBACK_PUBLIC_URL"],
            "missing_fields": self.missing_fields,
            "fields": {field: ("set" if self.values[field] else "missing") for field in (*CONFIG_FIELDS, *OPTIONAL_FIELDS)},
            "notes": [
                "真实密钥只从环境变量读取，不写入源码或聊天。",
                "当前已支持配置自检、签名校验、URL 验证解密、sync_msg 正文拉取和 send_msg 文本发送。",
                "语音、表情包、图片等媒体发送仍等待后续媒体上传链路。",
            ],
        }


def load_wecom_config_from_env(env=None):
    return WeComLiveConfig(env or os.environ)


def build_wecom_signature(token, timestamp, nonce, encrypted):
    raw = "".join(sorted([token or "", timestamp or "", nonce or "", encrypted or ""]))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def verify_wecom_signature(token, timestamp, nonce, encrypted, signature):
    expected = build_wecom_signature(token, timestamp, nonce, encrypted)
    return hmac.compare_digest(expected, (signature or "").lower())


def validate_encoding_aes_key(encoding_aes_key):
    if not encoding_aes_key:
        return "missing_encoding_aes_key"
    try:
        _decode_encoding_aes_key(encoding_aes_key)
    except WeComCryptoError:
        return "invalid_encoding_aes_key"
    return "ok"


def handle_callback_validation(config, query):
    echostr = (query.get("echostr") or "").strip()
    timestamp = (query.get("timestamp") or "").strip()
    nonce = (query.get("nonce") or "").strip()
    signature = (query.get("msg_signature") or "").strip()

    if not config.callback_configured:
        return {
            "status": "config_missing",
            "http_status": 400,
            "signature_valid": False,
            "missing_fields": config.callback_missing_fields,
            "reply_text": "",
        }

    signature_valid = verify_wecom_signature(config.token, timestamp, nonce, echostr, signature)
    if not signature_valid:
        return {
            "status": "signature_invalid",
            "http_status": 403,
            "signature_valid": False,
            "missing_fields": [],
            "reply_text": "",
        }

    try:
        reply_text = decrypt_wecom_message(config.values["WECOM_KF_ENCODING_AES_KEY"], echostr, config.values["WECOM_CORP_ID"])
    except WeComCryptoError as exc:
        return {
            "status": exc.code,
            "http_status": 403 if exc.code == "corp_id_mismatch" else 400,
            "signature_valid": True,
            "missing_fields": [],
            "reply_text": "",
            "next_action": "Check EncodingAESKey, CorpID, and callback query parameters in the WeCom console.",
        }

    return {
        "status": "ok",
        "http_status": 200,
        "signature_valid": True,
        "missing_fields": [],
        "reply_text": reply_text,
    }


def decrypt_encrypted_callback_event(config, query, body):
    timestamp = (query.get("timestamp") or "").strip()
    nonce = (query.get("nonce") or "").strip()
    signature = (query.get("msg_signature") or "").strip()

    if not config.callback_configured:
        return {
            "status": "config_missing",
            "http_status": 400,
            "signature_valid": False,
            "missing_fields": config.callback_missing_fields,
        }

    try:
        encrypted = extract_encrypt_from_xml(body)
    except WeComCryptoError as exc:
        return {
            "status": exc.code,
            "http_status": 400,
            "signature_valid": False,
            "body_has_encrypt": body_has_encrypt(body),
            "missing_fields": [],
        }

    signature_valid = verify_wecom_signature(config.token, timestamp, nonce, encrypted, signature)
    if not signature_valid:
        return {
            "status": "signature_invalid",
            "http_status": 403,
            "signature_valid": False,
            "body_has_encrypt": True,
            "missing_fields": [],
        }

    try:
        decrypted_xml = decrypt_wecom_message(
            config.values["WECOM_KF_ENCODING_AES_KEY"],
            encrypted,
            config.values["WECOM_CORP_ID"],
        )
        payload = parse_wecom_xml(decrypted_xml)
    except WeComCryptoError as exc:
        return {
            "status": exc.code,
            "http_status": 403 if exc.code == "corp_id_mismatch" else 400,
            "signature_valid": True,
            "body_has_encrypt": True,
            "missing_fields": [],
        }

    inbound = normalize_live_event(payload)
    return {
        "status": "ok",
        "http_status": 200,
        "signature_valid": True,
        "body_has_encrypt": True,
        "missing_fields": [],
        "inbound": inbound,
        "decrypted_xml": decrypted_xml,
    }


def extract_encrypt_from_xml(body):
    payload = parse_wecom_xml(body)
    encrypted = (payload.get("Encrypt") or "").strip()
    if not encrypted:
        raise WeComCryptoError("encrypt_missing", "Encrypt is required")
    return encrypted


def parse_wecom_xml(xml_text):
    normalized = normalize_wecom_xml_text(xml_text)
    try:
        root = ET.fromstring(normalized)
    except ET.ParseError as exc:
        raise WeComCryptoError("xml_invalid", "Invalid WeCom XML") from exc
    return {_xml_local_name(child.tag): child.text or "" for child in list(root)}


def normalize_wecom_xml_text(xml_text):
    text = str(xml_text or "").strip()
    parsed = parse_qs(text, keep_blank_values=True)
    for key in ("xml", "XML"):
        values = parsed.get(key)
        if values:
            text = values[0]
            break
    return text.strip().lstrip("\ufeff").strip()


def body_has_encrypt(body):
    try:
        return bool(extract_encrypt_from_xml(body))
    except WeComCryptoError:
        text = str(body or "")
        return "Encrypt" in text or "encrypt" in text or "%45%6E%63%72%79%70%74" in text


def _xml_local_name(tag):
    return str(tag).rsplit("}", 1)[-1]


def normalize_live_event(payload):
    msgtype = payload.get("msgtype") or payload.get("MsgType") or "text"
    text = payload.get("text") or {}
    content = text.get("content") if isinstance(text, dict) else ""
    if not content:
        content = payload.get("Content") or payload.get("content") or ""

    return {
        "channel": "wecom_live",
        "external_user_id": payload.get("external_userid") or payload.get("FromUserName") or payload.get("external_user_id") or "",
        "open_kfid": payload.get("open_kfid") or payload.get("OpenKfId") or "",
        "content_type": msgtype,
        "content": content,
        "event": payload.get("Event") or payload.get("event") or "",
        "message_token": payload.get("Token") or payload.get("token") or "",
        "source_message_id": payload.get("msgid") or payload.get("MsgId") or "",
        "raw": dict(payload),
    }


def build_text_send_payload(inbound, text):
    return {
        "touser": inbound["external_user_id"],
        "open_kfid": inbound["open_kfid"],
        "msgtype": "text",
        "text": {"content": text},
    }


def encrypt_wecom_message(encoding_aes_key, message, corp_id, random_bytes=None):
    key = _decode_encoding_aes_key(encoding_aes_key)
    random_bytes = random_bytes or os.urandom(16)
    if len(random_bytes) != 16:
        raise WeComCryptoError("invalid_random", "random_bytes must be 16 bytes")
    message_bytes = str(message).encode("utf-8")
    corp_bytes = str(corp_id).encode("utf-8")
    packed = random_bytes + struct.pack("!I", len(message_bytes)) + message_bytes + corp_bytes
    padded = _wechat_pad(packed)
    encrypted = _aes_256_cbc_encrypt(padded, key, key[:AES_BLOCK_SIZE])
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_wecom_message(encoding_aes_key, encrypted, expected_corp_id):
    key = _decode_encoding_aes_key(encoding_aes_key)
    try:
        ciphertext = base64.b64decode((encrypted or "").encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise WeComCryptoError("base64_invalid", "Encrypted payload is not valid base64") from exc
    try:
        padded = _aes_256_cbc_decrypt(ciphertext, key, key[:AES_BLOCK_SIZE])
        plain = _wechat_unpad(padded)
        if len(plain) < 20:
            raise WeComCryptoError("plaintext_invalid", "Plaintext is too short")
        message_length = struct.unpack("!I", plain[16:20])[0]
        message_start = 20
        message_end = message_start + message_length
        message = plain[message_start:message_end]
        corp_id = plain[message_end:].decode("utf-8")
    except WeComCryptoError:
        raise
    except Exception as exc:
        raise WeComCryptoError("decrypt_failed", "Unable to decrypt WeCom payload") from exc
    if corp_id != expected_corp_id:
        raise WeComCryptoError("corp_id_mismatch", "Decrypted CorpID does not match WECOM_CORP_ID")
    return message.decode("utf-8")


def _decode_encoding_aes_key(encoding_aes_key):
    if len(encoding_aes_key or "") != 43:
        raise WeComCryptoError("invalid_encoding_aes_key", "EncodingAESKey must be 43 characters")
    try:
        key = base64.b64decode((encoding_aes_key + "=").encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise WeComCryptoError("invalid_encoding_aes_key", "EncodingAESKey is not valid base64") from exc
    if len(key) != 32:
        raise WeComCryptoError("invalid_encoding_aes_key", "EncodingAESKey must decode to 32 bytes")
    return key


def _wechat_pad(data):
    pad_len = WECOM_PAD_BLOCK_SIZE - (len(data) % WECOM_PAD_BLOCK_SIZE)
    if pad_len == 0:
        pad_len = WECOM_PAD_BLOCK_SIZE
    return data + bytes([pad_len]) * pad_len


def _wechat_unpad(data):
    if not data:
        raise WeComCryptoError("padding_invalid", "Empty plaintext")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > WECOM_PAD_BLOCK_SIZE:
        raise WeComCryptoError("padding_invalid", "Invalid padding length")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise WeComCryptoError("padding_invalid", "Invalid padding bytes")
    return data[:-pad_len]


S_BOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

INV_S_BOX = (
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
)

RCON = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _aes_256_cbc_encrypt(data, key, iv):
    if len(key) != 32:
        raise WeComCryptoError("invalid_aes_key", "AES-256 key must be 32 bytes")
    if len(iv) != AES_BLOCK_SIZE or len(data) % AES_BLOCK_SIZE:
        raise WeComCryptoError("invalid_aes_input", "AES-CBC data and IV sizes are invalid")
    round_keys = _expand_key(key)
    previous = iv
    out = bytearray()
    for offset in range(0, len(data), AES_BLOCK_SIZE):
        block = bytes(left ^ right for left, right in zip(data[offset : offset + AES_BLOCK_SIZE], previous))
        encrypted = _aes_encrypt_block(block, round_keys)
        out.extend(encrypted)
        previous = encrypted
    return bytes(out)


def _aes_256_cbc_decrypt(data, key, iv):
    if len(key) != 32:
        raise WeComCryptoError("invalid_aes_key", "AES-256 key must be 32 bytes")
    if len(iv) != AES_BLOCK_SIZE or len(data) % AES_BLOCK_SIZE:
        raise WeComCryptoError("invalid_aes_input", "AES-CBC data and IV sizes are invalid")
    round_keys = _expand_key(key)
    previous = iv
    out = bytearray()
    for offset in range(0, len(data), AES_BLOCK_SIZE):
        block = data[offset : offset + AES_BLOCK_SIZE]
        decrypted = _aes_decrypt_block(block, round_keys)
        out.extend(left ^ right for left, right in zip(decrypted, previous))
        previous = block
    return bytes(out)


def _expand_key(key):
    nk = 8
    nb = 4
    nr = 14
    words = [list(key[i : i + 4]) for i in range(0, len(key), 4)]
    for i in range(nk, nb * (nr + 1)):
        temp = words[i - 1].copy()
        if i % nk == 0:
            temp = _sub_word(_rot_word(temp))
            temp[0] ^= RCON[i // nk]
        elif i % nk == 4:
            temp = _sub_word(temp)
        words.append([left ^ right for left, right in zip(words[i - nk], temp)])
    return [bytes(sum(words[round_index * nb : (round_index + 1) * nb], [])) for round_index in range(nr + 1)]


def _rot_word(word):
    return word[1:] + word[:1]


def _sub_word(word):
    return [S_BOX[value] for value in word]


def _aes_encrypt_block(block, round_keys):
    state = list(block)
    _add_round_key(state, round_keys[0])
    for round_index in range(1, 14):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[round_index])
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[14])
    return bytes(state)


def _aes_decrypt_block(block, round_keys):
    state = list(block)
    _add_round_key(state, round_keys[14])
    for round_index in range(13, 0, -1):
        _inv_shift_rows(state)
        _inv_sub_bytes(state)
        _add_round_key(state, round_keys[round_index])
        _inv_mix_columns(state)
    _inv_shift_rows(state)
    _inv_sub_bytes(state)
    _add_round_key(state, round_keys[0])
    return bytes(state)


def _add_round_key(state, round_key):
    for index in range(AES_BLOCK_SIZE):
        state[index] ^= round_key[index]


def _sub_bytes(state):
    for index, value in enumerate(state):
        state[index] = S_BOX[value]


def _inv_sub_bytes(state):
    for index, value in enumerate(state):
        state[index] = INV_S_BOX[value]


def _shift_rows(state):
    for row_index in range(1, 4):
        row = [state[column * 4 + row_index] for column in range(4)]
        row = row[row_index:] + row[:row_index]
        for column, value in enumerate(row):
            state[column * 4 + row_index] = value


def _inv_shift_rows(state):
    for row_index in range(1, 4):
        row = [state[column * 4 + row_index] for column in range(4)]
        row = row[-row_index:] + row[:-row_index]
        for column, value in enumerate(row):
            state[column * 4 + row_index] = value


def _mix_columns(state):
    for column in range(4):
        offset = column * 4
        a0, a1, a2, a3 = state[offset : offset + 4]
        state[offset] = _gmul(a0, 2) ^ _gmul(a1, 3) ^ a2 ^ a3
        state[offset + 1] = a0 ^ _gmul(a1, 2) ^ _gmul(a2, 3) ^ a3
        state[offset + 2] = a0 ^ a1 ^ _gmul(a2, 2) ^ _gmul(a3, 3)
        state[offset + 3] = _gmul(a0, 3) ^ a1 ^ a2 ^ _gmul(a3, 2)


def _inv_mix_columns(state):
    for column in range(4):
        offset = column * 4
        a0, a1, a2, a3 = state[offset : offset + 4]
        state[offset] = _gmul(a0, 14) ^ _gmul(a1, 11) ^ _gmul(a2, 13) ^ _gmul(a3, 9)
        state[offset + 1] = _gmul(a0, 9) ^ _gmul(a1, 14) ^ _gmul(a2, 11) ^ _gmul(a3, 13)
        state[offset + 2] = _gmul(a0, 13) ^ _gmul(a1, 9) ^ _gmul(a2, 14) ^ _gmul(a3, 11)
        state[offset + 3] = _gmul(a0, 11) ^ _gmul(a1, 13) ^ _gmul(a2, 9) ^ _gmul(a3, 14)


def _gmul(left, right):
    result = 0
    for _ in range(8):
        if right & 1:
            result ^= left
        high_bit = left & 0x80
        left = (left << 1) & 0xFF
        if high_bit:
            left ^= 0x1B
        right >>= 1
    return result
