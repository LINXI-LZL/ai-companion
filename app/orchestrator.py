from .media import resolve_media
from .multimodal import decide_mode
from .safety import classify_safety


def plan_reply(user_id, message, memories=None):
    safety = classify_safety(message)
    decision = decide_mode(message, safety)
    reply_text = _build_reply_text(message, memories or [], safety, decision)
    voice_script = _build_voice_script(reply_text, decision["voice_intent"])
    media = resolve_media(decision["mode"], decision["sticker_intent"], decision["voice_intent"])

    return {
        "user_id": user_id,
        "input_text": message,
        "reply_text": reply_text,
        "mode": decision["mode"],
        "safety_mode": safety["safety_mode"],
        "risk_level": safety["risk_level"],
        "sticker_intent": decision["sticker_intent"],
        "voice_intent": decision["voice_intent"],
        "voice_script": voice_script,
        "media": media,
        "memory_used": list(memories or []),
    }


def _build_reply_text(message, memories, safety, decision):
    if safety["safety_mode"]:
        return safety["reply_text"]

    text = message or ""
    prefix = "我会短点说，" if any("短回复" in memory for memory in memories) else ""

    if decision["mode"] == "text_plus_short_voice":
        return prefix + "你这不是矫情，是电量见底还硬撑。先别逼自己睡，陪你把脑子音量调小一点。"

    if decision["sticker_intent"] == "sticker_speechless":
        return prefix + "离谱，临下班改需求这种操作真的很会给人续命失败。你现在最想骂哪一句？"

    if decision["sticker_intent"] == "sticker_supportive_mocking":
        return prefix + "你这拖延小剧场又开播了，但先别把自己骂扁。现在只做最小一步，五分钟那种。"

    if decision["sticker_intent"] == "sticker_supportive_hug":
        return prefix + "难受是真的，不用先装没事。我在，今晚先不用一个人把这些情绪全吞下去。"

    if decision["sticker_intent"] == "sticker_reaction_mocking":
        return prefix + "你这个比喻很损但很准，精神电量 3%，还在努力蓝牙连接世界。"

    return prefix + "收到，今晚先不讲大道理。你把这坨事扔我这儿，我陪你拆一点点。"


def _build_voice_script(reply_text, voice_intent):
    if voice_intent == "voice_sleepy_companion":
        return "低一点声音说：" + reply_text
    if voice_intent == "voice_serious_grounding":
        return "认真平稳地说：" + reply_text
    return ""
