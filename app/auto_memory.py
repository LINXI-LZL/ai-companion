import re

from .safety import classify_safety


SHORT_REPLY_MEMORY = "用户喜欢短回复"
BITING_FRIEND_MEMORY = "用户接受损友式吐槽"
WORK_PRESSURE_MEMORY = "用户最近反复被工作/老板改需求困扰"
SLEEP_COMPANION_MEMORY = "用户常在睡前需要陪伴"
AI_NICKNAME_PREFIX = "智能体昵称："
EVENT_MEMORY_PREFIX = "用户近况："

SENSITIVE_KEYWORDS = (
    "身份证",
    "手机号",
    "电话号码",
    "银行卡",
    "住址",
    "地址",
    "密码",
    "密钥",
    "secret",
    "token",
    "api key",
    "apikey",
    "WECOM_",
)

SHORT_REPLY_KEYWORDS = ("短点", "短回复", "简单说", "别长篇大论", "说重点")
BITING_FRIEND_KEYWORDS = ("嘴欠", "毒舌", "损友", "损我", "吐槽狠点")
WORK_KEYWORDS = ("老板", "领导", "甲方", "需求", "临下班", "加班", "背锅", "塞活")
SLEEP_KEYWORDS = ("睡不着", "睡前", "晚安", "半夜", "深夜")
REPEAT_HINTS = ("又", "总是", "最近", "反复", "老是", "一直")
RECENT_EVENT_KEYWORDS = (
    "受伤",
    "疼",
    "痛",
    "摔",
    "磕",
    "烫",
    "划",
    "割",
    "流血",
    "难受",
    "生病",
    "感冒",
    "发烧",
    "睡不着",
    "失眠",
    "被骂",
    "挨骂",
    "吵架",
    "崩溃",
    "哭",
    "加班",
    "改需求",
    "被拒",
    "分手",
)
RECENT_EVENT_PATTERNS = (
    re.compile(r"^我(?P<time>刚才|刚刚|刚|今天|今晚|最近)(?P<event>[^？?。！!\n]{1,28})"),
    re.compile(r"^(?P<time>刚才|刚刚|刚|今天|今晚|最近)我(?P<event>[^？?。！!\n]{1,28})"),
)
QUESTION_WORDS = ("谁", "什么", "怎么", "为啥", "为什么", "吗", "嘛", "么")
AI_NICKNAME_PATTERNS = (
    re.compile(r"(?:以后|从现在起)?你(?:以后)?(?:就)?叫(?P<nickname>[A-Za-z0-9_\-\u4e00-\u9fff]{1,12})"),
    re.compile(r"(?:以后|从现在起)?你(?:就)?是(?P<nickname>[A-Za-z0-9_\-\u4e00-\u9fff]{1,12})"),
    re.compile(r"我(?:以后)?叫你(?P<nickname>[A-Za-z0-9_\-\u4e00-\u9fff]{1,12})"),
    re.compile(r"我给你(?:起名|取名)叫(?P<nickname>[A-Za-z0-9_\-\u4e00-\u9fff]{1,12})"),
    re.compile(r"你的名字(?:是|叫)(?P<nickname>[A-Za-z0-9_\-\u4e00-\u9fff]{1,12})"),
)
AI_NICKNAME_REJECT_KEYWORDS = (
    "谁",
    "什么",
    "不是",
    "是不是",
    "吗",
    "嘛",
    "么",
    "怎么",
    "为什么",
    "为啥",
    "笨蛋",
    "傻",
    "垃圾",
    "废物",
)


def infer_auto_memories(message, recent_messages=None):
    text = (message or "").strip()
    if not can_store_memory(text):
        return []

    memories = []
    if _has_any(text, SHORT_REPLY_KEYWORDS):
        memories.append(SHORT_REPLY_MEMORY)
    if _has_any(text, BITING_FRIEND_KEYWORDS):
        memories.append(BITING_FRIEND_MEMORY)
    if _should_remember_repeated_theme(text, recent_messages or [], WORK_KEYWORDS):
        memories.append(WORK_PRESSURE_MEMORY)
    if _should_remember_repeated_theme(text, recent_messages or [], SLEEP_KEYWORDS):
        memories.append(SLEEP_COMPANION_MEMORY)
    ai_nickname = _extract_ai_nickname(text)
    if ai_nickname:
        memories.append(AI_NICKNAME_PREFIX + ai_nickname)
    recent_event = _extract_recent_event(text)
    if recent_event:
        memories.append(EVENT_MEMORY_PREFIX + recent_event)

    return _dedupe(memories)


def can_store_memory(content):
    text = (content or "").strip()
    return bool(text) and not classify_safety(text)["safety_mode"] and not _looks_sensitive(text)


def _should_remember_repeated_theme(text, recent_messages, keywords):
    if not _has_any(text, keywords):
        return False
    if _has_any(text, REPEAT_HINTS):
        return True
    return sum(1 for item in recent_messages if _has_any(item.get("incoming_text", ""), keywords)) >= 1


def _looks_sensitive(text):
    lowered = text.lower()
    if any(keyword.lower() in lowered for keyword in SENSITIVE_KEYWORDS):
        return True
    if re.search(r"1[3-9]\d{9}", text):
        return True
    if re.search(r"\bsk-[A-Za-z0-9_-]{6,}", text):
        return True
    return False


def _extract_ai_nickname(text):
    if _is_question_like(text):
        return None
    for pattern in AI_NICKNAME_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        nickname = _clean_ai_nickname(match.group("nickname"))
        if _is_valid_ai_nickname(nickname):
            return nickname
    return None


def _extract_recent_event(text):
    if _is_question_like(text):
        return None
    for pattern in RECENT_EVENT_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        event = _clean_recent_event(match.group("event"))
        candidate = f"用户{match.group('time')}{event}"
        if _is_valid_recent_event(candidate):
            return candidate
    return None


def _clean_recent_event(event):
    return (event or "").strip().strip("「」“”\"'，,。.!！？? ")


def _is_valid_recent_event(candidate):
    if not candidate or len(candidate) > 36:
        return False
    if any(word in candidate for word in QUESTION_WORDS):
        return False
    if not _has_any(candidate, RECENT_EVENT_KEYWORDS):
        return False
    return can_store_memory(EVENT_MEMORY_PREFIX + candidate)


def _clean_ai_nickname(nickname):
    return (nickname or "").strip().strip("「」“”\"'，,。.!！？? ")


def _is_valid_ai_nickname(nickname):
    if not nickname or len(nickname) > 12:
        return False
    if any(keyword in nickname for keyword in AI_NICKNAME_REJECT_KEYWORDS):
        return False
    if "我" in nickname or "你" in nickname:
        return False
    return can_store_memory(AI_NICKNAME_PREFIX + nickname)


def _is_question_like(text):
    return any(mark in text for mark in ("?", "？")) or any(word in text for word in QUESTION_WORDS) or "你是谁" in text or "你叫什么" in text


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def _dedupe(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
