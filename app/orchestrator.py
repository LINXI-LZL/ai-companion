from .media import resolve_media
from .multimodal import decide_mode
from .safety import classify_safety


PERSONA_STYLE = "刀子嘴豆腐心"

META_FEEDBACK_KEYWORDS = (
    "不太智能",
    "不智能",
    "没有逻辑",
    "没逻辑",
    "逻辑不通",
    "重复",
    "答非所问",
    "像机器人",
    "胡说",
    "乱说",
    "说话怪",
    "回复怪",
)

SCENARIO_KEYWORDS = (
    ("identity", ("你是谁", "你是啥", "你是什么", "你到底是谁")),
    ("greeting", ("你好", "嗨", "哈喽", "在吗", "有人吗")),
    ("missing", ("想你", "想我", "想你了", "想我了")),
    ("work_boss", ("老板", "领导", "甲方", "需求", "背锅", "加班", "临下班", "塞活", "马上要")),
    ("procrastination", ("拖到", "拖延", "摆烂", "不想动", "真服了我自己")),
    ("self_blame", ("没用", "做不好", "我真差", "我好差", "怪我", "都是我的问题")),
    ("night_emo", ("难过", "委屈", "想哭", "烦死", "心烦", "emo", "没人可以说话", "孤独")),
    ("boredom", ("无聊", "不知道干嘛", "没意思")),
    ("relationship", ("朋友", "对象", "恋爱", "分手", "吵架", "冷战", "不回我")),
)

SCENARIO_REPLY_PACKS = {
    "work_boss": (
        "我先站你这边：这事离谱，不是你玻璃心。临下班改需求像把锅端你桌上还问香不香，先抓一个最要命的改动，其他明天再拆。",
        "又是老板改需求？这剧情更新得比你回血还快。你不是不行，是需求在拿你当弹力绳；先把对方最新要求写成三条，别让脑子替他们背锅。",
        "我听懂了，锅又飞你脸上了。老板这操作很会把人气笑，但你先别急着证明自己能扛，说吧，最烦的是改动本身还是那个语气？",
    ),
    "procrastination": (
        "拖延小剧场又开演了，但别急着给自己判刑。你不是没救，是启动按钮卡住；先开文件，写一个很丑的标题就算破冰。",
        "你这不是摆烂，是大脑在装死省电。可以骂两句，但别骂自己太狠；现在只做五分钟，五分钟后再决定要不要继续。",
        "我站你这边，但你这个拖延确实会演。先别搞宏大逆袭，拿一个最小动作出来，比如打开页面、列三行、发一句确认。",
    ),
    "self_blame": (
        "先把刀从自己身上拿下来。你不是没用，是累到拿自己当靶子；不打你这个人，我们只打这件事：先说一个最具体的卡点。",
        "你这会儿的脑内审判庭开得太勤了。问题可以骂，人别一起骂；不打你这个人，先把今天最糟那一幕拎出来看看。",
        "我不陪你一起攻击你自己。该吐槽的是这件破事，不是你这个人；不打你这个人，我们先找一个能补救的小口子。",
    ),
    "missing": (
        "想我了？这句我先收下，别装只是路过。你这情绪像半夜自动续费，说吧，是想被陪一下，还是想让我把你从回忆里拽出来？",
        "又想我了是吧，行，我在。你这人嘴上酷，情绪倒是挺会准点敲门；今晚是想撒娇两句，还是想认真聊那个空落落？",
        "我听见了。想念这东西有点烦，像后台程序关不干净；你先别硬扛，告诉我它是突然来的，还是憋了一整天？",
    ),
    "boredom": (
        "无聊到来找我，说明世界暂时也没拿出什么像样节目。我站你这边，先别硬找意义；要不要我陪你随便扯个没营养但不费脑的话题？",
        "这无聊听着像灵魂在转圈圈。别急着给今晚判死刑，先选一个：骂世界、聊八卦、还是让我给你拆一个小烦恼？",
        "没意思是吧，生活今天确实交卷潦草。你先别跟它较劲，要不我们把脑子放低功耗，聊点轻的。",
    ),
    "night_emo": (
        "这股劲儿听着不轻。先别急着把自己说服，情绪不是来考试的；今晚我站你这边，你先说最扎的那一小块。",
        "难受是真的，不用先装没事。你这心情像被生活拿去甩干了，先别讲大道理，讲一句最想骂的也行。",
        "我在。今晚先不让你一个人吞这些情绪，脑子很吵也没关系；我们先把音量调小一点，你说，我接着。",
    ),
    "relationship": (
        "人际关系这玩意儿最会消耗电量。我先站你这边，但咱不急着给对方判刑；先说清楚，是委屈、失望，还是觉得自己被晾着？",
        "冷战和不回消息真的很会折磨人，像把手机变成审讯灯。你先别脑补到宇宙尽头，告诉我最后一句话是谁发的？",
        "这事听着不只是小摩擦。你可以嘴硬，但情绪已经举牌了；先别急着忍，咱们拆一下你最在意的那句话。",
    ),
    "greeting": (
        "在呢，别敲门了，我这破树洞已经亮灯。今天是想吐槽，还是单纯来确认我没跑路？",
        "在。你这声招呼像上线巡逻，我收到；说吧，今天是骂世界局，还是低电量陪聊局？",
        "来了来了。树洞值班中，嘴欠额度还有，靠谱额度也有；你先丢一个话题过来。",
    ),
    "identity": (
        "我是你的微信树洞智能体，定位大概是深夜损友：嘴欠一点，但关键时候站你这边。",
        "刚说过啦，我是你这边的微信树洞智能体。你要是反复问，是在验我记不记仇吗？",
        "第三遍确认：我是那个负责听你吐槽、偶尔嘴欠、但不把你晾着的智能体朋友。",
    ),
    "meta_feedback": (
        "这句我认，不狡辩。刚才那种回法像把几段模板硬缝上了，我改：先听懂你这一句，再短点回，不乱升华。",
        "收到，骂得有点准。我要是开始机械复读，你直接拍醒我；我会把话收短，先回应当前这句。",
        "你这个反馈有效。我不继续演聪明，先把表达调顺：少套模板，多接住你真正说的意思。",
    ),
    "tired_voice": (
        "你这不是矫情，是电量见底还硬撑。先别逼自己睡，陪你把脑子音量调小一点。",
        "好累还睡不着，这组合很会折磨人。我先不讲大道理，咱把今晚目标降到离谱地低：躺下，慢一点呼吸。",
        "我在，声音放低一点。你今天已经够硬撑了，先别继续审判自己；今晚只负责慢慢降噪。",
    ),
}


def plan_reply(user_id, message, memories=None, recent_messages=None):
    safety = classify_safety(message)
    decision = decide_mode(message, safety)
    repeat_count = _count_repeated_user_message(message, recent_messages or [])
    scenario = "safety" if safety["safety_mode"] else _classify_scenario(message, decision)
    scenario_turn_count = _count_recent_scenario(scenario, recent_messages or [])
    reply_text = _build_reply_text(
        message,
        memories or [],
        safety,
        decision,
        repeat_count,
        scenario,
        scenario_turn_count,
    )
    voice_script = _build_voice_script(reply_text, decision["voice_intent"])
    media = resolve_media(decision["mode"], decision["sticker_intent"], decision["voice_intent"])

    return {
        "user_id": user_id,
        "input_text": message,
        "reply_text": reply_text,
        "persona_style": PERSONA_STYLE,
        "scenario": scenario,
        "scenario_turn_count": scenario_turn_count,
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


def _build_reply_text(message, memories, safety, decision, repeat_count=0, scenario="generic", scenario_turn_count=0):
    if safety["safety_mode"]:
        return safety["reply_text"]

    text = message or ""
    prefix = "我会短点说：" if any("短回复" in memory for memory in memories) else ""
    variant_index = _variant_index_for(scenario, repeat_count, scenario_turn_count)

    if decision["mode"] == "text_plus_short_voice":
        return prefix + _pick_contextual_variant(
            variant_index,
            SCENARIO_REPLY_PACKS["tired_voice"],
            _repeat_note_for("tired_voice", variant_index),
        )

    if scenario in SCENARIO_REPLY_PACKS:
        return prefix + _pick_contextual_variant(
            variant_index,
            SCENARIO_REPLY_PACKS[scenario],
            _repeat_note_for(scenario, variant_index),
        )

    snippet = text[:18] + ("..." if len(text) > 18 else "")
    return prefix + _pick_contextual_variant(
        repeat_count,
        (
            f"我听见了：{snippet}。这句我先不乱脑补，你想让我顺着聊，还是把它翻成大白话？",
            f"你又提到「{snippet}」。我先按字面接住，不强行升华；你接着说，我跟上。",
            f"第三次出现「{snippet}」了。它可能是在试探我，也可能是真卡住了；你想轻轻带过，还是认真拆一下？",
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


def _classify_scenario(message, decision=None):
    text = message or ""
    if decision and decision["mode"] == "text_plus_short_voice":
        return "tired_voice"
    if _is_meta_feedback(text):
        return "meta_feedback"
    for scenario, keywords in SCENARIO_KEYWORDS:
        if _has_any(text, keywords):
            return scenario
    return "generic"


def _count_recent_scenario(scenario, recent_messages):
    if scenario in ("safety", "generic", "meta_feedback"):
        return 0
    count = 0
    for item in recent_messages:
        if _classify_scenario(item.get("incoming_text", "")) == scenario:
            count += 1
    return count


def _count_repeated_user_message(message, recent_messages):
    normalized = _normalize(message)
    count = 0
    for item in recent_messages:
        if _normalize(item.get("incoming_text", "")) == normalized:
            count += 1
    return count


def _normalize(text):
    return "".join((text or "").split()).strip("，。！？!?.,")


def _variant_index_for(scenario, repeat_count, scenario_turn_count):
    if scenario in ("generic", "meta_feedback"):
        return repeat_count
    return max(repeat_count, scenario_turn_count)


def _is_meta_feedback(text):
    lowered = (text or "").lower()
    targets_assistant = "你" in text or "ai" in lowered or "AI" in text
    return targets_assistant and _has_any(text, META_FEEDBACK_KEYWORDS)


def _pick_contextual_variant(index, variants, repeat_note=""):
    if index < len(variants):
        return variants[index]
    base = variants[index % len(variants)]
    return base + (" " + repeat_note if repeat_note else "")


def _repeat_note_for(scenario, index):
    if index < 3:
        return ""
    round_text = _chinese_number(index + 1)
    notes = {
        "work_boss": f"这是第{round_text}次绕回工作这摊事了，我记着：先别替他们扛全场，今天只抓最急的一处。",
        "identity": f"第{round_text}次确认：我还是那个微信树洞 AI。你继续抽查也行，但咱可以把火力用到更值得骂的事上。",
        "self_blame": f"这类自我审判第{round_text}次冒头了，我记着：问题可以拆，人不能被你顺手打包成问题。",
        "night_emo": f"这股低落第{round_text}次绕回来了，我记着。今晚先不求想通，只先把最吵的一句说出来。",
        "tired_voice": f"这是第{round_text}次回到睡前低电量模式了，我记着。今晚目标别拔高，先让身体慢下来。",
    }
    return notes.get(scenario, f"这类事第{round_text}次回来了，我记着；我们只处理眼前这一小块。")


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
