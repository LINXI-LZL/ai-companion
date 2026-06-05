import re

from .safety import classify_safety


SHORT_REPLY_MEMORY = "用户喜欢短回复"
BITING_FRIEND_MEMORY = "用户接受损友式吐槽"
WORK_PRESSURE_MEMORY = "用户最近反复被工作/老板改需求困扰"
SLEEP_COMPANION_MEMORY = "用户常在睡前需要陪伴"

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


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def _dedupe(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
