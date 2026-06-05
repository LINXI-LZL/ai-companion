from datetime import datetime, timezone


DEFAULT_CHANNEL = "wecom_kf"
SUPPORTED_CONTENT_TYPES = {"text"}


def normalize_inbound_event(payload):
    content_type = (payload.get("content_type") or payload.get("MsgType") or "text").strip()
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValueError(f"unsupported content type: {content_type}")

    external_user_id = (payload.get("external_user_id") or payload.get("FromUserName") or "").strip()
    content = (payload.get("content") or payload.get("Content") or "").strip()
    if not external_user_id:
        raise ValueError("external user id is required")
    if not content:
        raise ValueError("content is required")

    return {
        "id": str(payload.get("message_id") or payload.get("MsgId") or ""),
        "channel": payload.get("channel") or DEFAULT_CHANNEL,
        "external_user_id": external_user_id,
        "content_type": content_type,
        "content": content,
        "received_at": _received_at(payload),
    }


def resolve_mock_user(store, inbound):
    handle = f"wechat:{inbound['external_user_id']}"
    user = store.get_user_by_handle(handle)
    if user:
        return user
    return store.create_user(handle, f"微信模拟用户 {inbound['external_user_id']}", allowed=True)


def build_outbound_message(inbound, plan):
    return {
        "channel": inbound["channel"],
        "external_user_id": inbound["external_user_id"],
        "source_message_id": inbound["id"],
        "message_type": "text",
        "text": plan["reply_text"],
        "mode": plan["mode"],
        "media_intent": plan.get("sticker_intent") or "none",
        "voice_intent": plan.get("voice_intent") or "none",
        "fallback_to_text": bool(plan.get("media", {}).get("fallback_to_text", False)),
        "send_policy": "local_mock_only",
    }


def _received_at(payload):
    raw_time = payload.get("received_at")
    if raw_time:
        return raw_time
    create_time = payload.get("CreateTime")
    if create_time:
        return datetime.fromtimestamp(int(create_time), timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()
