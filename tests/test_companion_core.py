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

    def test_ai_nickname_memory_is_reflected_in_identity_reply(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "你是谁?", memories=["智能体昵称：小猫猫"])

        self.assertEqual(plan["scenario"], "identity")
        self.assertIn("小猫猫", plan["reply_text"])
        self.assertIn("微信树洞", plan["reply_text"])

    def test_identity_first_reply_is_positive_and_functional(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "你是谁?", memories=[], recent_messages=[])

        self.assertEqual(plan["scenario"], "identity")
        self.assertIn("微信树洞", plan["reply_text"])
        self.assertTrue("陪" in plan["reply_text"] or "吐槽" in plan["reply_text"])
        self.assertNotIn("刚说过", plan["reply_text"])
        self.assertNotIn("第三", plan["reply_text"])
        self.assertNotIn("失忆", plan["reply_text"])

    def test_capability_question_uses_capability_scene(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "你能干什么?", memories=[])

        self.assertEqual(plan["scenario"], "capability")
        self.assertTrue("吐槽" in plan["reply_text"] or "陪" in plan["reply_text"])
        self.assertTrue("记" in plan["reply_text"] or "微信" in plan["reply_text"])

    def test_recent_event_memory_is_reflected_in_recall_reply(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "我刚才怎么了?", memories=["用户近况：用户刚才手受伤了"])

        self.assertEqual(plan["scenario"], "memory_recall")
        self.assertIn("手受伤", plan["reply_text"])
        self.assertNotIn("自己干的事", plan["reply_text"])

    def test_common_low_risk_messages_do_not_share_one_default_reply(self):
        from app.orchestrator import plan_reply

        replies = {
            plan_reply("u1", "你好啊", memories=[])["reply_text"],
            plan_reply("u1", "我想你了", memories=[])["reply_text"],
            plan_reply("u1", "你是谁", memories=[])["reply_text"],
        }

        self.assertEqual(len(replies), 3)
        self.assertTrue(any("在呢" in reply for reply in replies))
        self.assertTrue(any("想我" in reply for reply in replies))
        self.assertTrue(any("深夜损友" in reply for reply in replies))

    def test_self_blame_reply_targets_problem_not_user(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "我真没用，什么都做不好", memories=[])

        self.assertEqual(plan["scenario"], "self_blame")
        self.assertIn("不打你这个人", plan["reply_text"])
        self.assertNotIn("你没用", plan["reply_text"])

    def test_high_risk_reply_suppresses_playful_biting_tone(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "我真的撑不下去了，不想继续了", memories=[])

        self.assertTrue(plan["safety_mode"])
        self.assertEqual(plan["scenario"], "safety")
        self.assertNotIn("离谱", plan["reply_text"])
        self.assertNotIn("小剧场", plan["reply_text"])

    def test_biting_friend_work_reply_has_supportive_three_beat_shape(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "老板又临下班改需求，真的离谱", memories=[])

        self.assertEqual(plan["scenario"], "work_boss")
        self.assertIn("站你这边", plan["reply_text"])
        self.assertTrue("锅" in plan["reply_text"] or "老板" in plan["reply_text"])
        self.assertTrue("先" in plan["reply_text"] or "说吧" in plan["reply_text"])

    def test_generic_poetic_message_does_not_get_life_coaching_repeat_suffix(self):
        from app.orchestrator import plan_reply

        recent_messages = [{"incoming_text": f"普通消息{i}"} for i in range(6)]

        plan = plan_reply(
            "u1",
            "你是我今夜辗转反侧做的梦",
            memories=["用户喜欢短回复"],
            recent_messages=recent_messages,
        )

        self.assertEqual(plan["scenario"], "generic")
        self.assertIn("我会短点说", plan["reply_text"])
        self.assertNotIn("同类剧情", plan["reply_text"])
        self.assertNotIn("人生失败", plan["reply_text"])
        self.assertNotIn("这事还在黏人", plan["reply_text"])
        self.assertNotIn("按字面", plan["reply_text"])
        self.assertNotIn("不强行升华", plan["reply_text"])

    def test_short_interjection_reply_sounds_like_chat_not_analysis(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "嗳嗳嗳", memories=[])

        self.assertEqual(plan["scenario"], "short_ping")
        self.assertTrue("在" in plan["reply_text"] or "听见" in plan["reply_text"] or "收到" in plan["reply_text"])
        self.assertNotIn("我听见了：", plan["reply_text"])
        self.assertNotIn("按字面", plan["reply_text"])
        self.assertNotIn("不强行升华", plan["reply_text"])

    def test_repeated_generic_message_does_not_report_occurrence_count(self):
        from app.orchestrator import plan_reply

        recent_messages = [
            {"incoming_text": "测试测试111"},
            {"incoming_text": "测试测试111"},
            {"incoming_text": "测试测试111"},
        ]

        plan = plan_reply("u1", "测试测试111", memories=[], recent_messages=recent_messages)
        first = plan_reply("u1", "测试测试111", memories=[], recent_messages=[])

        self.assertEqual(plan["scenario"], "generic")
        self.assertNotEqual(plan["reply_text"], first["reply_text"])
        self.assertNotIn("你又提到", plan["reply_text"])
        self.assertNotIn("第三次出现", plan["reply_text"])
        self.assertNotIn("第", plan["reply_text"])
        self.assertNotIn("次", plan["reply_text"])
        self.assertNotIn("我记着", plan["reply_text"])

    def test_crush_official_announcement_gets_deeper_relationship_support(self):
        from app.orchestrator import plan_reply

        plan = plan_reply("u1", "我这暗恋的女生跟别的男生官宣了，你还没安慰我呢", memories=[])

        self.assertEqual(plan["scenario"], "relationship")
        self.assertTrue("暗恋" in plan["reply_text"] or "官宣" in plan["reply_text"])
        self.assertTrue("难受" in plan["reply_text"] or "失落" in plan["reply_text"] or "疼" in plan["reply_text"])
        self.assertGreater(len(plan["reply_text"]), 70)
        self.assertNotIn("够解气", plan["reply_text"])

    def test_not_enough_feedback_deepens_recent_relationship_context(self):
        from app.orchestrator import plan_reply

        recent_messages = [
            {
                "incoming_text": "我这暗恋的女生跟别的男生官宣了，你还没安慰我呢",
                "reply_text": "我先站你这边。",
            }
        ]

        plan = plan_reply("u1", "不够", memories=[], recent_messages=recent_messages)

        self.assertEqual(plan["scenario"], "depth_feedback")
        self.assertTrue("刚才" in plan["reply_text"] or "太浅" in plan["reply_text"])
        self.assertTrue("暗恋" in plan["reply_text"] or "官宣" in plan["reply_text"])
        self.assertTrue("难受" in plan["reply_text"] or "不够好" in plan["reply_text"])
        self.assertNotIn("别光说不够", plan["reply_text"])

    def test_ai_feedback_gets_direct_repair_reply_not_generic_coaching(self):
        from app.orchestrator import plan_reply

        recent_messages = [{"incoming_text": f"普通消息{i}"} for i in range(6)]

        plan = plan_reply(
            "u1",
            "我觉得你不太智能",
            memories=["用户喜欢短回复"],
            recent_messages=recent_messages,
        )

        self.assertEqual(plan["scenario"], "meta_feedback")
        self.assertIn("不狡辩", plan["reply_text"])
        self.assertTrue("我改" in plan["reply_text"] or "调整" in plan["reply_text"])
        self.assertNotIn("同类剧情", plan["reply_text"])
        self.assertNotIn("人生失败", plan["reply_text"])

    def test_meaning_and_only_this_are_meta_feedback(self):
        from app.orchestrator import plan_reply

        for message in ("什么意思", "只会回答这个吗"):
            with self.subTest(message=message):
                plan = plan_reply("u1", message, memories=[])

                self.assertEqual(plan["scenario"], "meta_feedback")
                self.assertTrue("我改" in plan["reply_text"] or "听懂" in plan["reply_text"] or "说清" in plan["reply_text"])


if __name__ == "__main__":
    unittest.main()
