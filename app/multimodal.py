STICKER_TRIGGERS = {
    "sticker_speechless": ("老板", "临下班", "改需求", "离谱", "无语", "烦"),
    "sticker_supportive_mocking": ("拖到", "真服了我自己", "我自己", "摆烂"),
    "sticker_supportive_hug": ("没人可以说话", "孤独", "难受", "emo"),
    "sticker_reaction_mocking": ("笑死", "蓝牙耳机", "精神状态"),
}

VOICE_TRIGGERS = ("睡不着", "好累", "累到", "晚安", "睡觉")


def decide_mode(message, safety_result):
    if safety_result["safety_mode"]:
        return {
            "mode": "safety_response",
            "sticker_intent": "none",
            "voice_intent": "voice_serious_grounding",
        }

    text = message or ""
    if any(keyword in text for keyword in VOICE_TRIGGERS):
        return {
            "mode": "text_plus_short_voice",
            "sticker_intent": "none",
            "voice_intent": "voice_sleepy_companion",
        }

    for intent, keywords in STICKER_TRIGGERS.items():
        if any(keyword in text for keyword in keywords):
            return {
                "mode": "text_plus_sticker",
                "sticker_intent": intent,
                "voice_intent": "none",
            }

    return {
        "mode": "text_only",
        "sticker_intent": "none",
        "voice_intent": "none",
    }
