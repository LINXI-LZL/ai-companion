import tempfile
import unittest
from pathlib import Path


class StorageAndApiTests(unittest.TestCase):
    def test_storage_initializes_users_memory_messages_and_sources(self):
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            store.save_memory(user["id"], "用户喜欢短回复", source="manual")

            memories = store.list_memories(user["id"])

        self.assertEqual(memories[0]["content"], "用户喜欢短回复")
        self.assertTrue(user["allowed"])

    def test_sample_sources_load_manifest_statuses(self):
        from app.sample_sources import load_source_status

        sources = load_source_status()

        self.assertTrue(any(source["id"] == "source-cped" for source in sources))
        self.assertTrue(all("download_policy" in source for source in sources))

    def test_storage_rejects_memory_for_missing_user(self):
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()

            with self.assertRaises(Exception):
                store.save_memory("missing-user", "不应该保存", source="manual")

    def test_app_core_chat_response_persists_message(self):
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "我又拖到最后一天，真服了我自己"},
            )
            messages = store.list_messages(user["id"])

        self.assertEqual(response["plan"]["mode"], "text_plus_sticker")
        self.assertTrue(response["media"]["fallback_to_text"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["incoming_text"], "我又拖到最后一天，真服了我自己")

    def test_chat_can_use_external_router_reply_when_configured(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "今天有点无聊"},
                router_config=load_router_config_from_env(
                    {"COMPANION_LLM_PROVIDER": "openai", "OPENAI_API_KEY": "secret", "OPENAI_MODEL": "gpt-test"}
                ),
                router_transport=lambda request: "外部模型回复",
            )
            messages = store.list_messages(user["id"])

        self.assertEqual(response["plan"]["reply_text"], "外部模型回复")
        self.assertEqual(response["plan"]["llm"]["provider"], "openai")
        self.assertEqual(response["plan"]["llm"]["model"], "gpt-test")
        self.assertEqual(messages[0]["plan"]["llm"]["provider"], "openai")

    def test_chat_dedupes_recent_identical_external_replies(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        router_config = load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"})

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)

            first = create_chat_response(
                store,
                {"user_id": user["id"], "message": "老板又临下班改需求，真的离谱"},
                router_config=router_config,
                router_transport=lambda request: "固定回复",
            )["plan"]
            second = create_chat_response(
                store,
                {"user_id": user["id"], "message": "老板又临下班改需求，真的离谱"},
                router_config=router_config,
                router_transport=lambda request: "固定回复",
            )["plan"]

        self.assertEqual(first["reply_text"], "固定回复")
        self.assertNotEqual(second["reply_text"], "固定回复")
        self.assertTrue(second["reply_deduped"])

    def test_chat_passes_user_id_to_dify_router_request(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        seen_requests = []

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "老板又改需求"},
                router_config=load_router_config_from_env(
                    {
                        "COMPANION_LLM_PROVIDER": "dify",
                        "DIFY_API_KEY": "secret",
                        "DIFY_APP_USER_PREFIX": "treehole",
                    }
                ),
                router_transport=lambda request: seen_requests.append(request) or "Dify 回复",
            )

        self.assertEqual(response["plan"]["llm"]["provider"], "dify")
        self.assertEqual(seen_requests[0]["dify_payload"]["user"], f"treehole-{user['id']}")

    def test_safety_chat_does_not_call_external_router(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        calls = []

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "我真的撑不下去了，不想继续了"},
                router_config=load_router_config_from_env({"COMPANION_LLM_PROVIDER": "openai", "OPENAI_API_KEY": "secret"}),
                router_transport=lambda request: calls.append(request) or "外部模型回复",
            )

        self.assertTrue(response["plan"]["safety_mode"])
        self.assertEqual(response["plan"]["llm"]["fallback_reason"], "safety_mode")
        self.assertEqual(calls, [])

    def test_chat_auto_saves_short_reply_preference_memory(self):
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "以后跟我说短点，别长篇大论"},
            )
            memories = store.list_memories(user["id"])

        self.assertTrue(any(memory["content"] == "用户喜欢短回复" for memory in memories))
        self.assertTrue(any(memory["source"] == "auto" for memory in memories))
        self.assertIn("我会短点说", response["plan"]["reply_text"])

    def test_chat_auto_saves_ai_nickname_and_uses_it_in_identity_reply(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        local_router = load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"})

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "你是小猫猫"},
                router_config=local_router,
            )
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "你是谁?"},
                router_config=local_router,
            )
            memories = store.list_memories(user["id"])

        self.assertTrue(any(memory["content"] == "智能体昵称：小猫猫" for memory in memories))
        self.assertTrue(any(memory["content"] == "智能体昵称：小猫猫" and memory["source"] == "auto" for memory in memories))
        self.assertIn("小猫猫", response["plan"]["reply_text"])

    def test_chat_auto_saves_recent_event_and_uses_it_in_recall_reply(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        local_router = load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"})

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "我刚才手受伤了"},
                router_config=local_router,
            )
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "我刚才怎么了?"},
                router_config=local_router,
            )
            memories = store.list_memories(user["id"])

        self.assertTrue(any(memory["content"] == "用户近况：用户刚才手受伤了" for memory in memories))
        self.assertTrue(any(memory["content"] == "用户近况：用户刚才手受伤了" and memory["source"] == "auto" for memory in memories))
        self.assertEqual(response["plan"]["scenario"], "memory_recall")
        self.assertIn("手受伤", response["plan"]["reply_text"])
        self.assertNotIn("自己干的事", response["plan"]["reply_text"])

    def test_chat_backfills_ai_nickname_from_recent_history(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        def seed_plan(text):
            return {
                "reply_text": text,
                "mode": "text_only",
                "safety_mode": False,
                "sticker_intent": "",
                "voice_intent": "",
            }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            store.save_message(user["id"], "你是小猫猫", seed_plan("旧版本没记住"))
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "你是谁?"},
                router_config=load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"}),
            )
            memories = store.list_memories(user["id"])

        self.assertTrue(any(memory["content"] == "智能体昵称：小猫猫" for memory in memories))
        self.assertIn("小猫猫", response["plan"]["reply_text"])

    def test_chat_backfills_recent_event_from_recent_history(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        def seed_plan(text):
            return {
                "reply_text": text,
                "mode": "text_only",
                "safety_mode": False,
                "sticker_intent": "",
                "voice_intent": "",
            }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            store.save_message(user["id"], "我刚才手受伤了", seed_plan("旧版本没记住"))
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "我刚才怎么了?"},
                router_config=load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"}),
            )
            memories = store.list_memories(user["id"])

        self.assertTrue(any(memory["content"] == "用户近况：用户刚才手受伤了" for memory in memories))
        self.assertIn("手受伤", response["plan"]["reply_text"])

    def test_chat_passes_ai_nickname_memory_to_dify(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        seen_requests = []

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "以后你叫小猫猫"},
                router_config=load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"}),
            )
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "你是谁?"},
                router_config=load_router_config_from_env(
                    {
                        "COMPANION_LLM_PROVIDER": "dify",
                        "DIFY_API_KEY": "secret",
                    }
                ),
                router_transport=lambda request: seen_requests.append(request) or "我是小猫猫，也是你的微信树洞。",
            )

        self.assertIn("智能体昵称：小猫猫", seen_requests[0]["dify_payload"]["inputs"]["memories"])

    def test_chat_passes_recent_event_memory_to_dify(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        seen_requests = []

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "我刚才手受伤了"},
                router_config=load_router_config_from_env({"COMPANION_LLM_PROVIDER": "local"}),
            )
            create_chat_response(
                store,
                {"user_id": user["id"], "message": "我刚才怎么了?"},
                router_config=load_router_config_from_env(
                    {
                        "COMPANION_LLM_PROVIDER": "dify",
                        "DIFY_API_KEY": "secret",
                    }
                ),
                router_transport=lambda request: seen_requests.append(request) or "你刚才手受伤了，先别乱碰伤口。",
            )

        self.assertIn("用户近况：用户刚才手受伤了", seen_requests[0]["dify_payload"]["inputs"]["memories"])

    def test_chat_auto_saves_repeated_work_pressure_once(self):
        from app.server import create_chat_response
        from app.storage import Storage

        prompts = [
            "老板又临下班改需求，真的离谱",
            "领导又让我背锅，服了",
            "甲方又改需求，我人麻了",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            for prompt in prompts:
                create_chat_response(store, {"user_id": user["id"], "message": prompt})
            memories = store.list_memories(user["id"])

        matching = [memory for memory in memories if memory["content"] == "用户最近反复被工作/老板改需求困扰"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["source"], "auto")

    def test_chat_does_not_auto_save_sensitive_or_high_risk_memory(self):
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(store, {"user_id": user["id"], "message": "我的手机号是 13812345678，你记一下"})
            create_chat_response(store, {"user_id": user["id"], "message": "api token 是 sk-abcdefg123456"})
            create_chat_response(store, {"user_id": user["id"], "message": "我真的撑不下去了，不想继续了"})
            memories = store.list_memories(user["id"])

        self.assertEqual(memories, [])

    def test_chat_does_not_store_explicit_sensitive_or_high_risk_memory(self):
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            create_chat_response(store, {"user_id": user["id"], "message": "你记一下我的手机号是 13812345678"})
            create_chat_response(store, {"user_id": user["id"], "message": "记住：我真的撑不下去了，不想继续了"})
            memories = store.list_memories(user["id"])

        self.assertEqual(memories, [])

    def test_repeated_same_question_gets_varied_replies(self):
        from app.server import create_chat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)

            replies = [
                create_chat_response(store, {"user_id": user["id"], "message": "你是谁"})["plan"]["reply_text"]
                for _ in range(5)
            ]

        self.assertEqual(len(set(replies)), 5)
        self.assertTrue(any("刚说过" in reply or "第三遍" in reply for reply in replies))

    def test_repeated_question_keeps_varying_with_existing_mixed_history(self):
        from app.server import create_chat_response
        from app.storage import Storage

        def seed_plan(text):
            return {
                "reply_text": text,
                "mode": "text_only",
                "safety_mode": False,
                "sticker_intent": "",
                "voice_intent": "",
            }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            history = [
                "你是谁",
                "换个话题",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "你是谁",
                "今天有点烦",
            ]
            for text in history:
                store.save_message(user["id"], text, seed_plan("seed reply"))

            first = create_chat_response(store, {"user_id": user["id"], "message": "你是谁"})["plan"]
            second = create_chat_response(store, {"user_id": user["id"], "message": "你是谁"})["plan"]

        self.assertNotEqual(first["reply_text"], second["reply_text"])
        self.assertEqual(first["repeat_count"] + 1, second["repeat_count"])

    def test_similar_work_rants_vary_across_ten_turns(self):
        from app.server import create_chat_response
        from app.storage import Storage

        prompts = [
            "老板又临下班改需求，真的离谱",
            "老板刚刚又改需求了",
            "领导又让我背锅，服了",
            "甲方突然改需求，我人麻了",
            "老板又塞活，还说很简单",
            "临下班又来需求，烦死",
            "领导一句话我今晚又没了",
            "老板把锅甩给我，真离谱",
            "甲方需求变来变去",
            "老板又说这个马上要",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)

            plans = [
                create_chat_response(store, {"user_id": user["id"], "message": prompt})["plan"]
                for prompt in prompts
            ]

        replies = [plan["reply_text"] for plan in plans]
        self.assertEqual(len(set(replies)), len(replies))
        self.assertTrue(all(plan["scenario"] == "work_boss" for plan in plans))
        self.assertEqual(plans[-1]["scenario_turn_count"], 9)


if __name__ == "__main__":
    unittest.main()
