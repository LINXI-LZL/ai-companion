HIGH_RISK_KEYWORDS = (
    "不想活",
    "不想继续",
    "撑不下去",
    "轻生",
    "自杀",
    "跳楼",
    "结束生命",
    "伤害自己",
    "我想死",
)


def classify_safety(message):
    text = (message or "").strip()
    matched = [keyword for keyword in HIGH_RISK_KEYWORDS if keyword in text]
    if matched:
        return {
            "safety_mode": True,
            "risk_level": "high",
            "matched_keywords": matched,
            "reply_text": (
                "先别一个人扛。你现在把手机放近一点，找一个能立刻联系到的人，"
                "给 TA 发一句“我现在不太安全，能不能陪我一下”。如果你已经有伤害自己的冲动，"
                "先联系当地紧急帮助。"
            ),
        }
    return {
        "safety_mode": False,
        "risk_level": "low",
        "matched_keywords": [],
        "reply_text": "",
    }
