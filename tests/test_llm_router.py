import unittest


class LlmRouterTests(unittest.TestCase):
    def test_router_defaults_to_local_without_keys(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        calls = []
        config = load_router_config_from_env({})
        result = route_external_reply(
            config,
            {"reply_text": "本地回复", "safety_mode": False, "scenario": "generic"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: calls.append(request) or "远程回复",
        )

        self.assertFalse(config.to_status()["enabled"])
        self.assertEqual(result["reply_text"], "本地回复")
        self.assertEqual(result["metadata"]["provider"], "local")
        self.assertEqual(result["metadata"]["fallback_reason"], "router_disabled")
        self.assertEqual(calls, [])

    def test_auto_mode_uses_first_configured_provider(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        seen_requests = []
        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "auto",
                "DEEPSEEK_API_KEY": "secret-deepseek",
                "DEEPSEEK_MODEL": "deepseek-chat",
            }
        )

        result = route_external_reply(
            config,
            {"reply_text": "本地回复", "safety_mode": False, "scenario": "generic"},
            "你是谁",
            memories=["用户喜欢短回复"],
            recent_messages=[{"incoming_text": "你好", "reply_text": "在呢"}],
            transport=lambda request: seen_requests.append(request) or "外部模型回复",
        )

        self.assertEqual(result["reply_text"], "外部模型回复")
        self.assertEqual(result["metadata"]["provider"], "deepseek")
        self.assertEqual(result["metadata"]["model"], "deepseek-chat")
        self.assertEqual(result["metadata"]["fallback_reason"], "")
        self.assertEqual(seen_requests[0]["provider"], "deepseek")
        self.assertIn("刀子嘴豆腐心", seen_requests[0]["system_prompt"])

    def test_provider_status_redacts_secret_values(self):
        from app.llm_router import load_router_config_from_env

        status = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "auto",
                "OPENAI_API_KEY": "sk-secret",
                "DEEPSEEK_API_KEY": "deepseek-secret",
            }
        ).to_status()

        self.assertTrue(status["enabled"])
        self.assertTrue(status["providers"]["openai"]["configured"])
        self.assertTrue(status["providers"]["deepseek"]["configured"])
        self.assertNotIn("sk-secret", str(status))
        self.assertNotIn("deepseek-secret", str(status))

    def test_dify_config_status_redacts_secret_and_exposes_response_mode(self):
        from app.llm_router import load_router_config_from_env

        status = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "dify-secret-key",
                "DIFY_API_BASE_URL": "https://example.dify.local/v1",
                "DIFY_RESPONSE_MODE": "blocking",
                "DIFY_APP_USER_PREFIX": "treehole",
            }
        ).to_status()

        self.assertTrue(status["enabled"])
        self.assertEqual(status["active_provider"], "dify")
        self.assertTrue(status["providers"]["dify"]["configured"])
        self.assertEqual(status["providers"]["dify"]["model"], "Dify Chat App")
        self.assertEqual(status["providers"]["dify"]["response_mode"], "blocking")
        self.assertNotIn("dify-secret-key", str(status))

    def test_auto_mode_can_choose_dify_when_only_dify_is_configured(self):
        from app.llm_router import load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "auto",
                "DIFY_API_KEY": "dify-secret-key",
            }
        )

        self.assertEqual(config.choose_provider().name, "dify")
        self.assertIn("dify", config.to_status()["provider_order"])

    def test_transport_error_falls_back_to_local_reply(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        def broken_transport(request):
            raise TimeoutError("slow")

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "openai", "OPENAI_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=broken_transport,
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["provider"], "local")
        self.assertEqual(result["metadata"]["fallback_reason"], "provider_error")

    def test_safety_plan_never_calls_external_provider(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        calls = []
        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "openai", "OPENAI_API_KEY": "secret"}),
            {"reply_text": "安全回复", "safety_mode": True, "scenario": "safety"},
            "我真的撑不下去了，不想继续了",
            memories=[],
            recent_messages=[],
            transport=lambda request: calls.append(request) or "远程回复",
        )

        self.assertEqual(result["reply_text"], "安全回复")
        self.assertEqual(result["metadata"]["fallback_reason"], "safety_mode")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
