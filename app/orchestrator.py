from .media import resolve_media
from .multimodal import decide_mode
from .safety import classify_safety


def plan_reply(user_id, message, memories=None, recent_messages=None):
    safety = classify_safety(message)
    decision = decide_mode(message, safety)
    repeat_count = _count_repeated_user_message(message, recent_messages or [])
    reply_text = _build_reply_text(message, memories or [], safety, decision, repeat_count)
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
        "repeat_count": repeat_count,
    }


def _build_reply_text(message, memories, safety, decision, repeat_count=0):
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

    if _has_any(text, ("你好", "嗨", "哈喽", "在吗", "有人吗")):
        return prefix + "在呢，别敲门了，我这破树洞已经亮灯。今天是想吐槽，还是单纯来确认我没跑路？"

    if _has_any(text, ("想你", "想我", "想你了", "想我了")):
        return prefix + "想我了？可以，今晚这句我先收下。别硬装酷了，说吧，是哪一阵情绪突然拐回来找你。"

    if _has_any(text, ("你是谁", "你是啥", "你是什么", "你到底是谁")):
        return prefix + _pick_repeat_variant(
            repeat_count,
            (
                "我是你的微信树洞智能体，定位大概是深夜损友：嘴欠一点，但关键时候站你这边。",
                "刚说过啦，我是你这边的微信树洞智能体。你要是反复问，是在验我记不记仇吗？",
                "第三遍确认：我是那个负责听你吐槽、偶尔嘴欠、但不把你晾着的智能体朋友。",
            ),
        )

    if _has_any(text, ("无聊", "不知道干嘛", "没意思")):
        return prefix + "无聊到来找我，说明世界暂时也没拿出什么像样节目。要不要我陪你随便扯两句？"

    if _has_any(text, ("难过", "委屈", "想哭", "烦死", "心烦")):
        return prefix + "这股劲儿听着不轻。先别急着把自己说服，今晚可以先承认：确实挺难受的。"

    snippet = text[:18] + ("..." if len(text) > 18 else "")
    return prefix + _pick_repeat_variant(
        repeat_count,
        (
            f"我听见了：{snippet}。先放我这儿，别急着总结人生失败，我们一点点拆。",
            f"你又提了一遍「{snippet}」，说明它还在脑子里转。那我们别绕了，先抓最烦的那一块。",
            f"第三次出现「{snippet}」了，我记下：这事不是路过，是卡住了。你想先骂它，还是先拆它？",
        ),
    )


def _build_voice_script(reply_text, voice_intent):
    if voice_intent == "voice_sleepy_companion":
        return "低一点声音说：" + reply_text
    if voice_intent == "voice_serious_grounding":
        return "认真平稳地说：" + reply_text
    return ""


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def _count_repeated_user_message(message, recent_messages):
    normalized = _normalize(message)
    count = 0
    for item in recent_messages:
        if _normalize(item.get("incoming_text", "")) == normalized:
            count += 1
    return count


def _normalize(text):
    return "".join((text or "").split()).strip("，。！？!?.,")


def _pick_repeat_variant(repeat_count, variants):
    if repeat_count < len(variants):
        return variants[repeat_count]
    base = variants[-1].replace("第三遍确认：", "")
    return f"第{_chinese_number(repeat_count + 1)}次确认：{base}不过你一直问同一个问题，我猜你不是没听见，是想看我会不会复读机上身。"


def _chinese_number(value):
    digits = "零一二三四五六七八九"
    if value < 10:
        return digits[value]
    if value == 10:
        return "十"
    if value < 20:
        return "十" + digits[value % 10]
    if value < 100:
        tens = value // 10
        ones = value % 10
        return digits[tens] + "十" + (digits[ones] if ones else "")
    return str(value)
