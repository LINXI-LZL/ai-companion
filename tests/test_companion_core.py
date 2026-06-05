import unittest


class CompanionCoreTests(unittest.TestCase):
    def test_high_risk_message_uses_safety_mode(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "我真的撑不下去了，不想继续了", memories=[])

        self.assertTrue(plan["safety_mode"])
        self.assertEqual(plan["mode"], "safety_response")
        self.assertEqual(plan["sticker_intent"], "none")
        self.assertIn("先别一个人扛", plan["reply_text"])

    def test_low_risk_work_rant_uses_sticker_intent(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "老板又临下班改需求，真的离谱", memories=[])

        self.assertFalse(plan["safety_mode"])
        self.assertEqual(plan["mode"], "text_plus_sticker")
        self.assertEqual(plan["sticker_intent"], "sticker_speechless")
        self.assertIn("离谱", plan["reply_text"])

    def test_late_night_tired_message_uses_voice_script(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "今天好累，但睡不着", memories=[])

        self.assertEqual(plan["mode"], "text_plus_short_voice")
        self.assertEqual(plan["voice_intent"], "voice_sleepy_companion")
        self.assertTrue(plan["voice_script"])

    def test_memory_can_be_reflected_in_reply(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "今天又开始emo", memories=["用户喜欢短回复"])

        self.assertIn("我会短点说", plan["reply_text"])


if __name__ == "__main__":
    unittest.main()
