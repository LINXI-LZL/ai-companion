import hashlib
import os


CONFIG_FIELDS = (
    "WECOM_CORP_ID",
    "WECOM_KF_SECRET",
    "WECOM_KF_TOKEN",
    "WECOM_KF_ENCODING_AES_KEY",
    "WECOM_OPEN_KFID",
)

OPTIONAL_FIELDS = ("WECOM_CALLBACK_PUBLIC_URL",)


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
    def configured(self):
        return len(self.missing_fields) == 0

    def to_status(self):
        return {
            "channel": "wecom_live",
            "configured": self.configured,
            "ready_for_real_callback": False,
            "crypto_status": "missing_wxbizmsgcrypt",
            "send_mode": "payload_only",
            "public_callback_url": self.values["WECOM_CALLBACK_PUBLIC_URL"],
            "missing_fields": self.missing_fields,
            "fields": {field: ("set" if self.values[field] else "missing") for field in (*CONFIG_FIELDS, *OPTIONAL_FIELDS)},
            "notes": [
                "真实密钥只从环境变量读取，不写入源码或聊天。",
                "当前已支持配置自检、签名校验、开发明文事件和发送载荷构造。",
                "真实企业微信 URL 验证仍需接入官方 WXBizMsgCrypt 兼容加解密库。",
            ],
        }


def load_wecom_config_from_env(env=None):
    return WeComLiveConfig(env or os.environ)


def build_wecom_signature(token, timestamp, nonce, encrypted):
    raw = "".join(sorted([token or "", timestamp or "", nonce or "", encrypted or ""]))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def verify_wecom_signature(token, timestamp, nonce, encrypted, signature):
    expected = build_wecom_signature(token, timestamp, nonce, encrypted)
    return expected == (signature or "").lower()


def handle_callback_validation(config, query):
    echostr = (query.get("echostr") or "").strip()
    timestamp = (query.get("timestamp") or "").strip()
    nonce = (query.get("nonce") or "").strip()
    signature = (query.get("msg_signature") or "").strip()

    if not config.configured:
        return {
            "status": "config_missing",
            "http_status": 400,
            "signature_valid": False,
            "missing_fields": config.missing_fields,
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

    return {
        "status": "crypto_not_configured",
        "http_status": 501,
        "signature_valid": True,
        "missing_fields": [],
        "reply_text": "",
        "next_action": "Install or vendor the official WXBizMsgCrypt compatible library to decrypt echostr.",
    }


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
