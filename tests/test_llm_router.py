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

    def test_dify_response_mode_defaults_to_blocking_for_unsupported_values(self):
        from app.llm_router import load_router_config_from_env

        status = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
                "DIFY_RESPONSE_MODE": "streaming",
            }
        ).to_status()

        self.assertEqual(status["providers"]["dify"]["response_mode"], "blocking")

    def test_dify_request_uses_chat_messages_payload_shape(self):
        from app.llm_router import build_provider_request, load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
                "DIFY_APP_USER_PREFIX": "treehole",
            }
        )
        provider = config.providers["dify"]

        request = build_provider_request(
            provider,
            {
                "reply_text": "本地兜底",
                "safety_mode": False,
                "scenario": "work_boss",
                "mode": "text_plus_sticker",
                "sticker_intent": "sticker_speechless",
                "voice_intent": "none",
            },
            "老板又临下班改需求，真的离谱",
            ["用户喜欢短回复"],
            [{"incoming_text": "你好", "reply_text": "在呢"}],
            user_id="owner",
        )

        self.assertEqual(request["provider"], "dify")
        self.assertEqual(request["message"], "老板又临下班改需求，真的离谱")
        self.assertEqual(request["dify_payload"]["query"], "老板又临下班改需求，真的离谱")
        self.assertEqual(request["dify_payload"]["response_mode"], "blocking")
        self.assertEqual(request["dify_payload"]["user"], "treehole-owner")
        self.assertEqual(request["dify_payload"]["inputs"]["persona_style"], "刀子嘴豆腐心")
        self.assertEqual(request["dify_payload"]["inputs"]["scenario"], "work_boss")
        self.assertEqual(request["dify_payload"]["inputs"]["mode"], "text_plus_sticker")
        self.assertEqual(request["dify_payload"]["inputs"]["media_intent"], "sticker_speechless")
        self.assertEqual(request["dify_payload"]["inputs"]["voice_intent"], "none")
        self.assertEqual(request["dify_payload"]["inputs"]["local_reply"], "本地兜底")
        self.assertIn("用户喜欢短回复", request["dify_payload"]["inputs"]["memories"])
        self.assertIn("用户：你好", request["dify_payload"]["inputs"]["recent_history"])

    def test_dify_recent_history_redacts_sensitive_previous_turns(self):
        from app.llm_router import build_provider_request, load_router_config_from_env

        provider = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
            }
        ).providers["dify"]

        request = build_provider_request(
            provider,
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "继续聊",
            [],
            [
                {"incoming_text": "我的手机号是 13812345678", "reply_text": "别把手机号发出来"},
                {"incoming_text": "api token 是 sk-abcdefg123456", "reply_text": "这个别发给别人"},
                {"incoming_text": "老板又改需求", "reply_text": "这事确实烦"},
            ],
            user_id="owner",
        )

        history = request["dify_payload"]["inputs"]["recent_history"]
        self.assertNotIn("13812345678", history)
        self.assertNotIn("sk-abcdefg123456", history)
        self.assertIn("[已省略敏感或高风险内容]", history)
        self.assertIn("老板又改需求", history)

    def test_dify_memories_redacts_sensitive_entries(self):
        from app.llm_router import build_provider_request, load_router_config_from_env

        provider = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
            }
        ).providers["dify"]

        request = build_provider_request(
            provider,
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "继续聊",
            ["用户喜欢短回复", "用户手机号是 13812345678", "api token 是 sk-abcdefg123456"],
            [],
            user_id="owner",
        )

        memories = request["dify_payload"]["inputs"]["memories"]
        self.assertIn("用户喜欢短回复", memories)
        self.assertIn("[已省略敏感或高风险内容]", memories)
        self.assertNotIn("13812345678", memories)
        self.assertNotIn("sk-abcdefg123456", memories)

    def test_non_dify_provider_request_does_not_include_dify_payload(self):
        from app.llm_router import build_provider_request, load_router_config_from_env

        provider = load_router_config_from_env(
            {"OPENAI_API_KEY": "secret"}
        ).providers["openai"]

        request = build_provider_request(
            provider,
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            [],
            [],
        )

        self.assertNotIn("dify_payload", request)
        self.assertIn("system_prompt", request)
        self.assertIn("user_prompt", request)

    def test_dify_call_posts_chat_messages_and_reads_answer(self):
        from unittest.mock import patch

        from app.llm_router import _call_provider, build_provider_request, load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
                "DIFY_API_BASE_URL": "https://dify.example/v1",
            }
        )
        provider = config.providers["dify"]
        request = build_provider_request(
            provider,
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你是谁",
            [],
            [],
            user_id="owner",
        )

        with patch(
            "app.llm_router._post_json",
            return_value={"answer": "我是你的微信树洞 AI。", "conversation_id": "conv-1"},
        ) as post_json:
            raw = _call_provider(provider, request, 8)

        self.assertEqual(raw["text"], "我是你的微信树洞 AI。")
        self.assertEqual(raw["conversation_id"], "conv-1")
        url, headers, payload, timeout_seconds = post_json.call_args.args
        self.assertEqual(url, "https://dify.example/v1/chat-messages")
        self.assertEqual(headers["Authorization"], "Bearer secret")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertIn("DifySmokeTest", headers["User-Agent"])
        self.assertEqual(payload["response_mode"], "blocking")
        self.assertEqual(payload["query"], "你是谁")
        self.assertEqual(timeout_seconds, 8)

    def test_dify_thinking_output_falls_back_to_local_reply(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: {"answer": "<think>internal reasoning</think>\n你好"},
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["provider"], "local")
        self.assertEqual(result["metadata"]["fallback_reason"], "debug_output")

    def test_transport_error_falls_back_to_local_reply(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        def broken_transport(request):
            raise RuntimeError("boom")

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

    def test_provider_timeout_has_specific_fallback_reason(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: (_ for _ in ()).throw(TimeoutError("slow")),
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["provider"], "local")
        self.assertEqual(result["metadata"]["fallback_reason"], "provider_timeout")

    def test_provider_output_too_long_falls_back_to_local_reply(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env(
                {
                    "COMPANION_LLM_PROVIDER": "dify",
                    "DIFY_API_KEY": "secret",
                    "COMPANION_LLM_MAX_OUTPUT_CHARS": "12",
                }
            ),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: "这是一段明显超过长度限制的外部回复",
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["fallback_reason"], "output_too_long")

    def test_dify_conversation_id_is_copied_to_metadata_without_changing_text(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: {"text": "Dify 回复", "conversation_id": "conv-1"},
        )

        self.assertEqual(result["reply_text"], "Dify 回复")
        self.assertEqual(result["metadata"]["conversation_id"], "conv-1")

    def test_non_dify_provider_does_not_copy_conversation_id_metadata(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "openai", "OPENAI_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: {"text": "外部回复", "conversation_id": "conv-openai"},
        )

        self.assertEqual(result["reply_text"], "外部回复")
        self.assertNotIn("conversation_id", result["metadata"])

    def test_real_provider_timeout_has_specific_fallback_reason(self):
        from unittest.mock import patch

        from app.llm_router import load_router_config_from_env, route_external_reply

        with patch("app.llm_router.urllib.request.urlopen", side_effect=TimeoutError("slow")):
            result = route_external_reply(
                load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
                {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
                "你好",
                memories=[],
                recent_messages=[],
            )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["fallback_reason"], "provider_timeout")

    def test_urlerror_wrapped_timeout_has_specific_fallback_reason(self):
        from unittest.mock import patch
        import urllib.error

        from app.llm_router import load_router_config_from_env, route_external_reply

        with patch("app.llm_router.urllib.request.urlopen", side_effect=urllib.error.URLError(TimeoutError("timed out"))):
            result = route_external_reply(
                load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
                {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
                "你好",
                memories=[],
                recent_messages=[],
            )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["fallback_reason"], "provider_timeout")

    def test_generic_urlerror_stays_provider_error(self):
        from unittest.mock import patch
        import urllib.error

        from app.llm_router import load_router_config_from_env, route_external_reply

        with patch("app.llm_router.urllib.request.urlopen", side_effect=urllib.error.URLError("dns failed")):
            result = route_external_reply(
                load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
                {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
                "你好",
                memories=[],
                recent_messages=[],
            )

        self.assertEqual(result["reply_text"], "本地兜底")
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
