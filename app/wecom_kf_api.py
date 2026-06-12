import json
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT_SECONDS = 8
DEFAULT_SYNC_LIMIT = 100


class WeComKfApiError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def sync_kf_text_messages(config, message_token, open_kfid="", transport=None):
    if not config.values["WECOM_CORP_ID"] or not config.values["WECOM_KF_SECRET"]:
        raise WeComKfApiError("missing_sync_config", "WECOM_CORP_ID and WECOM_KF_SECRET are required for sync_msg")
    if not message_token:
        raise WeComKfApiError("missing_message_token", "callback Token is required for sync_msg")

    access_token = fetch_access_token(config, transport=transport)
    payload = {
        "token": message_token,
        "limit": DEFAULT_SYNC_LIMIT,
        "voice_format": 0,
    }
    resolved_open_kfid = open_kfid or config.open_kfid
    if resolved_open_kfid:
        payload["open_kfid"] = resolved_open_kfid

    response = _send_request(
        {
            "name": "sync_msg",
            "method": "POST",
            "url": f"https://qyapi.weixin.qq.com/cgi-bin/kf/sync_msg?access_token={quote(access_token)}",
            "json": payload,
            "timeout": DEFAULT_TIMEOUT_SECONDS,
        },
        transport=transport,
    )
    _raise_for_wecom_error(response, default_code="sync_msg_failed")
    return response


def send_kf_text_message(config, payload, transport=None):
    if not config.values["WECOM_CORP_ID"] or not config.values["WECOM_KF_SECRET"]:
        raise WeComKfApiError("missing_send_config", "WECOM_CORP_ID and WECOM_KF_SECRET are required for send_msg")

    message = _normalize_text_send_payload(config, payload)
    access_token = fetch_access_token(config, transport=transport)
    response = _send_request(
        {
            "name": "send_msg",
            "method": "POST",
            "url": f"https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token={quote(access_token)}",
            "json": message,
            "timeout": DEFAULT_TIMEOUT_SECONDS,
        },
        transport=transport,
    )
    _raise_for_wecom_error(response, default_code="send_msg_failed")
    return response


def fetch_access_token(config, transport=None):
    response = _send_request(
        {
            "name": "get_access_token",
            "method": "GET",
            "url": (
                "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
                f"?corpid={quote(config.values['WECOM_CORP_ID'])}"
                f"&corpsecret={quote(config.values['WECOM_KF_SECRET'])}"
            ),
            "timeout": DEFAULT_TIMEOUT_SECONDS,
        },
        transport=transport,
    )
    _raise_for_wecom_error(response, default_code="access_token_failed")
    access_token = response.get("access_token")
    if not access_token:
        raise WeComKfApiError("access_token_missing", "WeCom gettoken response did not include access_token")
    return access_token


def _normalize_text_send_payload(config, payload):
    payload = dict(payload or {})
    text = dict(payload.get("text") or {})
    payload["text"] = text
    if not payload.get("open_kfid") and config.open_kfid:
        payload["open_kfid"] = config.open_kfid
    if not payload.get("touser"):
        raise WeComKfApiError("missing_send_touser", "touser is required for send_msg")
    if not payload.get("open_kfid"):
        raise WeComKfApiError("missing_send_open_kfid", "open_kfid is required for send_msg")
    if payload.get("msgtype") != "text":
        raise WeComKfApiError("unsupported_send_msgtype", "only text send_msg is supported in this round")
    if not text.get("content"):
        raise WeComKfApiError("missing_send_text", "text.content is required for send_msg")
    return payload


def _send_request(request, transport=None):
    if transport:
        return transport(dict(request))
    try:
        return _default_transport(request)
    except Exception as exc:
        raise WeComKfApiError("wecom_api_transport_failed", "WeCom API request failed") from exc


def _default_transport(request):
    data = None
    headers = {"Accept": "application/json"}
    if request.get("json") is not None:
        data = json.dumps(request["json"], ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    http_request = Request(request["url"], data=data, headers=headers, method=request.get("method", "GET"))
    with urlopen(http_request, timeout=request.get("timeout", DEFAULT_TIMEOUT_SECONDS)) as response:
        body = response.read().decode("utf-8")
    return json.loads(body or "{}")


def _raise_for_wecom_error(response, default_code):
    errcode = response.get("errcode", 0)
    if errcode not in (0, "0"):
        raise WeComKfApiError(default_code, f"WeCom API error {errcode}: {response.get('errmsg', '')}")
