from .auto_memory import AI_NICKNAME_PREFIX, EVENT_MEMORY_PREFIX
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
    "什么意思",
    "什么鬼",
    "听不懂",
    "看不懂",
    "只会回答这个",
    "只会说这个",
    "就会这个",
    "像机器人",
    "胡说",
    "乱说",
    "说话怪",
    "回复怪",
)

DIRECT_META_FEEDBACK_EXACT = (
    "什么意思",
    "什么鬼",
    "啥意思",
    "听不懂",
    "看不懂",
)

DIRECT_META_FEEDBACK_PHRASES = (
    "只会回答这个",
    "只会说这个",
    "就会这个",
)

DEPTH_FEEDBACK_EXACT = (
    "不够",
    "还不够",
    "不够啊",
    "没安慰到我",
    "没安慰我",
    "太浅了",
)

DEPTH_FEEDBACK_PHRASES = (
    "说深一点",
    "认真安慰",
    "认真点",
    "展开说",
    "讲深一点",
)

SCENARIO_KEYWORDS = (
    ("identity", ("你是谁", "你是啥", "你是什么", "你到底是谁", "你叫什么", "你叫啥", "你的名字")),
    ("capability", ("你能干什么", "你能干嘛", "你会什么", "你有什么功能", "你能做什么", "你可以干什么", "你可以干嘛", "能陪我干嘛")),
    ("greeting", ("你好", "嗨", "哈喽", "在吗", "有人吗")),
    ("missing", ("想你", "想我", "想你了", "想我了")),
    ("work_boss", ("老板", "领导", "甲方", "需求", "背锅", "加班", "临下班", "塞活", "马上要")),
    ("procrastination", ("拖到", "拖延", "摆烂", "不想动", "真服了我自己")),
    ("self_blame", ("没用", "做不好", "我真差", "我好差", "怪我", "都是我的问题")),
    ("night_emo", ("难过", "委屈", "想哭", "烦死", "心烦", "emo", "没人可以说话", "孤独")),
    ("boredom", ("无聊", "不知道干嘛", "没意思")),
    ("relationship", ("朋友", "对象", "恋爱", "分手", "吵架", "冷战", "不回我", "暗恋", "喜欢的人", "官宣", "男生", "女生")),
)

SCENARIO_REPLY_PACKS = {
    "work_boss": (
        "我先站你这边：这事离谱，不是你玻璃心。临下班改需求像把锅端你桌上还问香不香，先抓一个最要命的改动，其他明天再拆。",
        "又是老板改需求？这剧情更新得比你回血还快。你不是不行，是需求在拿你当弹力绳；先把对方最新要求写成三条，别让脑子替他们背锅。",
        "我听懂了，锅又飞你脸上了。老板这操作很会把人气笑，但你先别急着证明自己能扛，说吧，最烦的是改动本身还是那个语气？",
        "这活听着就像临时把桌子掀了还让你负责摆盘。先别急着全接，挑一个最影响交付的点回过去，让他们先确认。",
        "服了，这种“很简单”通常最不简单。你先别替他把模糊话翻译成十个任务，抓住一句：到底今天必须改哪一块？",
        "这锅甩得挺有抛物线天赋。我站你这边，但现在先别跟情绪硬刚，先把责任边界写清楚，别让它默默长到你头上。",
        "甲方这需求像风向标成精，转得人脑壳疼。你先别追着风跑，问一句最终版以哪条为准，留个痕。",
        "你今晚又被一句话偷走了是吧。先骂它两秒，然后把任务切到最小：能延期的延期，不能延期的只做核心。",
        "老板这句“马上要”很会把人血压叫醒。你先别直接冲刺，回他一个范围和时间，让锅别悄悄变成你的私人财产。",
        "需求变来变去，最累的是你还得装成系统稳定运行。别装了，先把变化点列出来，让对方确认优先级。",
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
    "short_ping": (
        "在，我听见了。你这是喊我上线，还是想确认我没跑？",
        "收到。别光在门口敲两下，下一句呢？",
        "我在呢。你这声像信号测试，也像有话憋着，来，说。",
    ),
    "greeting": (
        "在呢，别敲门了，我这破树洞已经亮灯。今天是想吐槽，还是单纯来确认我没跑路？",
        "在。你这声招呼像上线巡逻，我收到；说吧，今天是骂世界局，还是低电量陪聊局？",
        "来了来了。树洞值班中，嘴欠额度还有，靠谱额度也有；你先丢一个话题过来。",
    ),
    "identity": (
        "我是你的微信树洞 AI，深夜损友型陪聊：能接住吐槽、帮你把乱糟糟的话捋顺，也会记一点安全的轻量小事。",
        "刚说过啦，我是你这边的微信树洞智能体。你要是反复问，是在验我记不记仇吗？",
        "第三遍确认：我是那个负责听你吐槽、偶尔嘴欠、但不把你晾着的智能体朋友。",
    ),
    "capability": (
        "我能做的事不复杂但挺实用：陪你吐槽、接情绪、把混乱的话捋顺，也能记住一些安全的轻量小事，比如你给我起的名字或刚才发生了什么。",
        "我的主业是当你的微信树洞：你丢烦心事，我先站你这边；你问刚才聊了什么，我尽量按记忆接上；你想短点，我也能收住。",
        "你可以把我当一个会回消息的陪聊好友：能听你骂老板、陪你低电量聊天、帮你整理一句要怎么说，还能在安全范围内记住关键上下文。",
    ),
    "meta_feedback": (
        "这句我认，不狡辩。刚才没说清的话我改：先听懂你这一句，再短点回，不乱升华。",
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
    recent_messages = recent_messages or []
    safety = classify_safety(message)
    decision = decide_mode(message, safety)
    repeat_count = _count_repeated_user_message(message, recent_messages)
    scenario = "safety" if safety["safety_mode"] else _classify_scenario(message, decision, recent_messages)
    scenario_turn_count = _count_recent_scenario(scenario, recent_messages)
    context_topic = _latest_substantial_user_message(recent_messages) if scenario == "depth_feedback" else ""
    reply_text = _build_reply_text(
        message,
        memories or [],
        safety,
        decision,
        repeat_count,
        scenario,
        scenario_turn_count,
        recent_messages,
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
        "reply_deduped": False,
        "context_topic": context_topic,
    }


def avoid_recent_reply_repeat(plan, recent_messages):
    """Replace an exact repeat with another local variant before persistence."""
    current = _normalize_reply(plan.get("reply_text", ""))
    if not current:
        return False
    recent_replies = {
        _normalize_reply(item.get("reply_text", ""))
        for item in list(recent_messages or [])[:6]
        if _normalize_reply(item.get("reply_text", ""))
    }
    if current not in recent_replies:
        return False

    for candidate in _reply_candidates_for_plan(plan):
        if not candidate:
            continue
        if _normalize_reply(candidate) == current:
            continue
        if _normalize_reply(candidate) in recent_replies:
            continue
        plan["reply_text"] = candidate
        plan["voice_script"] = _build_voice_script(candidate, plan.get("voice_intent", ""))
        plan["reply_deduped"] = True
        return True
    return False


def _build_reply_text(
    message,
    memories,
    safety,
    decision,
    repeat_count=0,
    scenario="generic",
    scenario_turn_count=0,
    recent_messages=None,
):
    if safety["safety_mode"]:
        return safety["reply_text"]

    text = message or ""
    prefix = "我会短点说：" if any("短回复" in memory for memory in memories) else ""
    variant_index = _variant_index_for(scenario, repeat_count, scenario_turn_count)
    ai_nickname = _extract_ai_nickname(memories)

    if scenario == "identity" and ai_nickname:
        return prefix + _build_named_identity_reply(ai_nickname, variant_index)
    if scenario == "memory_recall":
        recent_event = _extract_recent_event_memory(memories)
        if recent_event:
            return prefix + _build_memory_recall_reply(recent_event, variant_index)
        return prefix + "我这边没抓到可靠的轻量记忆，不硬编。你把刚才那句再丢我一遍，我这次记牢。"
    if scenario == "depth_feedback":
        return prefix + _build_depth_feedback_reply(recent_messages or [], variant_index)

    if decision["mode"] == "text_plus_short_voice":
        return prefix + _pick_contextual_variant(
            variant_index,
            SCENARIO_REPLY_PACKS["tired_voice"],
            _repeat_note_for("tired_voice", variant_index),
        )

    if scenario == "relationship" and _looks_like_unrequited_loss(text):
        return prefix + _build_unrequited_loss_reply(variant_index)

    if scenario in SCENARIO_REPLY_PACKS:
        return prefix + _pick_contextual_variant(
            variant_index,
            SCENARIO_REPLY_PACKS[scenario],
            _repeat_note_for(scenario, variant_index),
        )

    if _looks_poetic_or_ambiguous(text):
        return prefix + _pick_contextual_variant(
            variant_index,
            (
                "这句话有点像半夜递过来的小纸条，我收到了。你想顺着这个梦聊，还是让我把它翻成大白话？",
                "嗯，这句挺暧昧，也挺会绕人。你是想让我接着演，还是认真问我一句？",
                "这话我不乱拆，先放在桌上。你继续说，我跟着这个气氛走。",
            ),
        )

    return prefix + _pick_contextual_variant(
        repeat_count,
        (
            "这句有点突然，我先接住。你想顺着聊，还是让我帮你翻成大白话？",
            "懂，你先别急着解释。把下一句丢过来，我跟着你走。",
            "我在，先不瞎猜。你是想轻轻带过，还是认真拆一下？",
            "收到。这个我先不乱编意义，你给我一点方向，我就能接着陪你聊。",
            "行，我接住了。你现在是想试试我反应，还是这句话背后真有点东西？",
            "我跟上。你不用把话一次说完整，先丢一小块也行。",
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


def _classify_scenario(message, decision=None, recent_messages=None):
    text = message or ""
    if decision and decision["mode"] == "text_plus_short_voice":
        return "tired_voice"
    if _is_memory_recall_question(text):
        return "memory_recall"
    if _is_depth_feedback(text):
        return "depth_feedback"
    if _is_meta_feedback(text):
        return "meta_feedback"
    if _is_short_ping(text):
        return "short_ping"
    for scenario, keywords in SCENARIO_KEYWORDS:
        if _has_any(text, keywords):
            return scenario
    return "generic"


def _count_recent_scenario(scenario, recent_messages):
    if scenario in ("safety", "generic", "meta_feedback", "depth_feedback"):
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
    if scenario in ("generic", "meta_feedback", "depth_feedback"):
        return repeat_count
    return max(repeat_count, scenario_turn_count)


def _is_meta_feedback(text):
    lowered = (text or "").lower()
    if _is_direct_meta_feedback(text):
        return True
    targets_assistant = "你" in text or "ai" in lowered or "AI" in text
    return targets_assistant and _has_any(text, META_FEEDBACK_KEYWORDS)


def _is_direct_meta_feedback(text):
    normalized = _normalize(text)
    return normalized in DIRECT_META_FEEDBACK_EXACT or _has_any(text, DIRECT_META_FEEDBACK_PHRASES)


def _is_depth_feedback(text):
    normalized = _normalize(text)
    return normalized in DEPTH_FEEDBACK_EXACT or _has_any(text or "", DEPTH_FEEDBACK_PHRASES)


def _extract_ai_nickname(memories):
    for memory in memories:
        if memory.startswith(AI_NICKNAME_PREFIX):
            nickname = memory[len(AI_NICKNAME_PREFIX) :].strip()
            if nickname:
                return nickname
    return ""


def _build_named_identity_reply(nickname, variant_index):
    return _pick_contextual_variant(
        variant_index,
        (
            f"我是{nickname}，也是你的微信树洞 AI。负责陪你吐槽、接住情绪、记一点安全的小上下文。",
            f"又抽查我？我是{nickname}，你亲口给我扣上的名号；微信树洞这班我还在值。",
            f"第三次确认：{nickname}在这儿，微信树洞也在这儿。负责听你吐槽，偶尔嘴欠，但不把你晾着。",
        ),
    )


def _extract_recent_event_memory(memories):
    for memory in memories:
        if memory.startswith(EVENT_MEMORY_PREFIX):
            event = memory[len(EVENT_MEMORY_PREFIX) :].strip()
            if event:
                return event
    return ""


def _build_memory_recall_reply(recent_event, variant_index):
    spoken_event = _event_to_spoken_recall(recent_event)
    if any(keyword in recent_event for keyword in ("受伤", "疼", "痛", "摔", "磕", "烫", "划", "割", "流血")):
        variants = (
            f"你刚才说{spoken_event}。先别逞强，伤口能冲就冲干净，能贴就贴上；疼得厉害就找人看看。",
            f"我记着呢：你刚才说{spoken_event}。别拿自己当铁打的，先处理伤口，再来跟我贫。",
            f"不是你凭空失忆，是我这里记着：{spoken_event}。先把伤口弄稳，别一边疼一边还硬撑。",
        )
    else:
        variants = (
            f"你刚才说{spoken_event}。我记着，不是让你一个人把这段糊弄过去。",
            f"我这边记着：{spoken_event}。别急着怀疑自己，咱就按这件事往下聊。",
            f"刚才那段我没丢：{spoken_event}。你要继续说，我接着听。",
        )
    return _pick_contextual_variant(variant_index, variants)


def _build_unrequited_loss_reply(variant_index):
    variants = (
        "这个真的会难受。暗恋最疼的点，不是她官宣这一条消息本身，而是你心里那段没来得及说出口的期待突然被判出局了。先别装大度，今晚你可以酸、可以失落，但别把这件事翻译成“我不够好”。",
        "我认真安慰你，不拿梗糊弄：看到暗恋的人和别人官宣，像是自己默默排了很久的队，突然发现窗口关了。你难受很正常，先允许自己失落，别急着祝福，也别拿自己和那个男生硬比。",
        "这事扎人，因为它不是简单的“她谈恋爱了”，而是你偷偷放在心里的位置被别人占了。你现在难受不是小题大做，是那点期待真的落空了；先别审判自己，今晚先把这口气慢慢吐出来。",
    )
    return _pick_contextual_variant(variant_index, variants)


def _build_depth_feedback_reply(recent_messages, variant_index):
    topic = _latest_substantial_user_message(recent_messages)
    if _looks_like_unrequited_loss(topic):
        variants = (
            "你说不够是对的，我刚才回浅了。暗恋的人官宣，疼的不是一条动态，是你心里那段还没说出口的期待被按了暂停。你现在难受，不代表你输了；先别急着体面，今晚允许自己酸、失落，但不要把它变成“我不够好”的判决。",
            "嗯，刚才那句确实没接住你。你要的不是一句“别难过”，是有人承认：看着暗恋的人跟别人官宣，真的会像自己被悄悄排除在故事外。先别逼自己洒脱，你可以难受一会儿，我在这儿陪你把这股劲儿放下来。",
            "不够，那我认真补上。你难受的核心不是那个男生多厉害，而是你喜欢她这件事还没来得及有结果，就被现实突然盖章了。别急着跟他比，也别急着骂自己没出息；今晚先承认一句：我就是很失落。",
        )
        return _pick_contextual_variant(variant_index, variants)
    variants = (
        "你说不够是对的，我刚才太浅了。你要的不是一句俏皮话，是有人认真接住你。我们往深一点说：最刺你的不是表面这句话，而是它戳到了你心里哪块？",
        "收到，我不继续糊弄。刚才我只接了表面情绪，没往里走；你把最难受的那一小块丢出来，我认真陪你拆，不拿模板盖过去。",
        "嗯，是我没给够。那我们别急着换话题：这件事真正让你卡住的，是委屈、失望、不甘心，还是觉得自己没被看见？",
    )
    return _pick_contextual_variant(variant_index, variants)


def _event_to_spoken_recall(recent_event):
    text = recent_event.replace("用户", "你", 1)
    for prefix in ("你刚才", "你刚刚", "你刚", "你今天", "你今晚", "你最近"):
        if text.startswith(prefix):
            return text[len(prefix) :]
    return text


def _is_memory_recall_question(text):
    if not any(marker in text for marker in ("刚才", "刚刚", "前面", "之前")):
        return False
    return any(marker in text for marker in ("怎么了", "咋了", "发生什么", "说什么", "我说了什么", "什么事"))


def _pick_contextual_variant(index, variants, repeat_note=""):
    if index < len(variants):
        return variants[index]
    base = variants[index % len(variants)]
    return base + (" " + repeat_note if repeat_note else "")


def _reply_candidates_for_plan(plan):
    scenario = plan.get("scenario") or "generic"
    prefix = "我会短点说：" if any("短回复" in memory for memory in plan.get("memory_used", [])) else ""
    ai_nickname = _extract_ai_nickname(plan.get("memory_used", []))
    if scenario == "identity" and ai_nickname:
        return [prefix + _build_named_identity_reply(ai_nickname, index) for index in range(6)]
    if scenario == "memory_recall":
        recent_event = _extract_recent_event_memory(plan.get("memory_used", []))
        if not recent_event:
            return []
        return [prefix + _build_memory_recall_reply(recent_event, index) for index in range(6)]
    if scenario == "depth_feedback":
        context_topic = plan.get("context_topic", "")
        context = [{"incoming_text": context_topic}] if context_topic else []
        return [prefix + _build_depth_feedback_reply(context, index) for index in range(6)]
    if scenario == "relationship" and _looks_like_unrequited_loss(plan.get("input_text", "")):
        return [prefix + _build_unrequited_loss_reply(index) for index in range(6)]
    if scenario in SCENARIO_REPLY_PACKS:
        return [
            prefix + _pick_contextual_variant(index, SCENARIO_REPLY_PACKS[scenario], _repeat_note_for(scenario, index))
            for index in range(6)
        ]
    text = plan.get("input_text", "")
    if _looks_poetic_or_ambiguous(text):
        variants = (
            "这句话有点像半夜递过来的小纸条，我收到了。你想顺着这个梦聊，还是让我把它翻成大白话？",
            "嗯，这句挺暧昧，也挺会绕人。你是想让我接着演，还是认真问我一句？",
            "这话我不乱拆，先放在桌上。你继续说，我跟着这个气氛走。",
        )
    else:
        variants = (
            "这句有点突然，我先接住。你想顺着聊，还是让我帮你翻成大白话？",
            "懂，你先别急着解释。把下一句丢过来，我跟着你走。",
            "我在，先不瞎猜。你是想轻轻带过，还是认真拆一下？",
            "收到。这个我先不乱编意义，你给我一点方向，我就能接着陪你聊。",
            "行，我接住了。你现在是想试试我反应，还是这句话背后真有点东西？",
            "我跟上。你不用把话一次说完整，先丢一小块也行。",
        )
    return [prefix + _pick_contextual_variant(index, variants) for index in range(6)]


def _normalize_reply(text):
    return " ".join((text or "").split()).strip()


def _looks_like_unrequited_loss(text):
    text = text or ""
    return _has_any(text, ("暗恋", "喜欢的人", "官宣")) and _has_any(text, ("男生", "女生", "别人", "别的", "官宣"))


def _latest_substantial_user_message(recent_messages):
    for item in recent_messages or []:
        text = item.get("incoming_text", "")
        if len(_normalize(text)) <= 2:
            continue
        if _is_depth_feedback(text) or _is_meta_feedback(text):
            continue
        return text
    return ""


def _repeat_note_for(scenario, index):
    if index < 3:
        return ""
    notes = {
        "work_boss": "我记住这个模式了：先别替他们扛全场，今天只抓最急的一处。",
        "identity": "我还在，微信树洞这班也还没下。你继续抽查也行，但咱可以把火力用到更值得骂的事上。",
        "self_blame": "我记住这个苗头了：问题可以拆，人不能被你顺手打包成问题。",
        "night_emo": "我记着这股低落。今晚先不求想通，只先把最吵的一句说出来。",
        "tired_voice": "我记着你现在是低电量模式。今晚目标别拔高，先让身体慢下来。",
    }
    return notes.get(scenario, "我记着这个方向；我们只处理眼前这一小块。")


def _is_short_ping(text):
    normalized = _normalize(text)
    if not normalized:
        return False
    if _has_any(normalized, ("能听见", "听得见", "听见我", "收到没", "在不在", "还在吗")):
        return True
    ping_chars = set("嗳诶欸嗯啊喂哈嘿哎唉呀哟?")
    return len(normalized) <= 6 and all(char in ping_chars for char in normalized)


def _looks_poetic_or_ambiguous(text):
    return _has_any(text or "", ("今夜", "辗转", "反侧", "梦", "月亮", "星星")) and len(text or "") <= 32
