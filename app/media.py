def resolve_media(mode, sticker_intent, voice_intent):
    if mode == "safety_response":
        return {
            "fallback_to_text": False,
            "asset_type": "safety",
            "asset_id": None,
            "notice": "Safety mode disables playful media.",
        }
    if sticker_intent and sticker_intent != "none":
        return {
            "fallback_to_text": True,
            "asset_type": "sticker",
            "asset_id": None,
            "notice": "Sticker asset is deferred; showing intent and text fallback.",
        }
    if voice_intent and voice_intent != "none":
        return {
            "fallback_to_text": True,
            "asset_type": "voice",
            "asset_id": None,
            "notice": "Voice synthesis is deferred; showing voice script fallback.",
        }
    return {
        "fallback_to_text": False,
        "asset_type": "text",
        "asset_id": None,
        "notice": "Text-only reply.",
    }
