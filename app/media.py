def resolve_media(mode, sticker_intent, voice_intent):
    if mode == "safety_response":
        return {
            "fallback_to_text": False,
            "asset_type": "safety",
            "asset_id": None,
            "notice": "安全模式下不发送玩笑式表情或语音。",
        }
    if sticker_intent and sticker_intent != "none":
        return {
            "fallback_to_text": True,
            "asset_type": "sticker",
            "asset_id": None,
            "notice": "真实表情包素材暂未接入，当前先显示表情意图并用文字兜底。",
        }
    if voice_intent and voice_intent != "none":
        return {
            "fallback_to_text": True,
            "asset_type": "voice",
            "asset_id": None,
            "notice": "真实语音合成暂未接入，当前先显示短语音脚本并用文字兜底。",
        }
    return {
        "fallback_to_text": False,
        "asset_type": "text",
        "asset_id": None,
        "notice": "纯文字回复。",
    }
