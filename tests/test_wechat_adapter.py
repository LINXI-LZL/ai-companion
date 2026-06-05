import tempfile
import unittest
from pathlib import Path


class WeChatAdapterTests(unittest.TestCase):
    def test_normalizes_text_event_and_builds_outbound_message(self):
        from app.wechat_adapter import build_outbound_message, normalize_inbound_event

        inbound = normalize_inbound_event(
            {
                "FromUserName": "external-owner",
                "MsgType": "text",
                "Content": "老板又临下班改需求，真的离谱",
                "MsgId": "wechat-msg-1",
                "CreateTime": 1780648000,
            }
        )
        outbound = build_outbound_message(
            inbound,
            {
                "reply_text": "离谱，先骂一句再拆。",
                "mode": "text_plus_sticker",
                "sticker_intent": "sticker_speechless",
                "voice_intent": "none",
                "media": {"fallback_to_text": True},
            },
        )

        self.assertEqual(inbound["channel"], "wecom_kf")
        self.assertEqual(inbound["external_user_id"], "external-owner")
        self.assertEqual(inbound["content_type"], "text")
        self.assertEqual(inbound["content"], "老板又临下班改需求，真的离谱")
        self.assertEqual(outbound["channel"], "wecom_kf")
        self.assertEqual(outbound["external_user_id"], "external-owner")
        self.assertEqual(outbound["message_type"], "text")
        self.assertEqual(outbound["text"], "离谱，先骂一句再拆。")
        self.assertEqual(outbound["media_intent"], "sticker_speechless")
        self.assertTrue(outbound["fallback_to_text"])

    def test_mock_wechat_inbound_uses_companion_flow(self):
        from app.server import create_mock_wechat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_mock_wechat_response(
                store,
                {
                    "FromUserName": "external-owner",
                    "MsgType": "text",
                    "Content": "今天好累，但睡不着",
                    "MsgId": "wechat-msg-2",
                },
            )
            user = store.get_user_by_handle("wechat:external-owner")
            messages = store.list_messages(user["id"])

        self.assertEqual(response["inbound"]["content"], "今天好累，但睡不着")
        self.assertEqual(response["outbound"]["message_type"], "text")
        self.assertEqual(response["outbound"]["voice_intent"], "voice_sleepy_companion")
        self.assertEqual(len(messages), 1)
        self.assertIn("睡", messages[0]["reply_text"])

    def test_wecom_live_config_status_redacts_secret_values(self):
        from app.wecom_live import load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "super-secret-value",
                "WECOM_KF_TOKEN": "token-value",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
                "WECOM_CALLBACK_PUBLIC_URL": "https://example.com/api/wecom-live/callback",
            }
        )
        status = config.to_status()

        self.assertTrue(status["configured"])
        self.assertEqual(status["channel"], "wecom_live")
        self.assertNotIn("super-secret-value", str(status))
        self.assertNotIn("token-value", str(status))
        self.assertEqual(status["fields"]["WECOM_KF_SECRET"], "set")
        self.assertEqual(status["public_callback_url"], "https://example.com/api/wecom-live/callback")

    def test_wecom_live_config_reports_missing_fields(self):
        from app.wecom_live import load_wecom_config_from_env

        status = load_wecom_config_from_env({"WECOM_CORP_ID": "ww-corp"}).to_status()

        self.assertFalse(status["configured"])
        self.assertIn("WECOM_KF_SECRET", status["missing_fields"])
        self.assertIn("WECOM_KF_TOKEN", status["missing_fields"])
        self.assertEqual(status["fields"]["WECOM_CORP_ID"], "set")

    def test_wecom_live_signature_uses_sorted_token_timestamp_nonce_encrypt(self):
        from app.wecom_live import build_wecom_signature, verify_wecom_signature

        signature = build_wecom_signature("token", "1700000000", "nonce", "encrypted")

        self.assertEqual(signature, "a976d3f9651ff9c34c56c6f9774c36bca10ec1de")
        self.assertTrue(verify_wecom_signature("token", "1700000000", "nonce", "encrypted", signature))
        self.assertFalse(verify_wecom_signature("token", "1700000000", "nonce", "tampered", signature))

    def test_wecom_live_callback_preflight_requires_crypto_for_real_echostr(self):
        from app.wecom_live import handle_callback_validation, load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": "encrypted",
            "msg_signature": "a976d3f9651ff9c34c56c6f9774c36bca10ec1de",
        }

        result = handle_callback_validation(config, query)

        self.assertEqual(result["status"], "crypto_not_configured")
        self.assertTrue(result["signature_valid"])
        self.assertEqual(result["http_status"], 501)

    def test_wecom_live_normalizes_dev_plaintext_event_and_send_payload(self):
        from app.wecom_live import build_text_send_payload, normalize_live_event

        inbound = normalize_live_event(
            {
                "channel": "wecom_live",
                "external_userid": "external-owner",
                "open_kfid": "wkf-123",
                "msgtype": "text",
                "text": {"content": "老板又临下班改需求，真的离谱"},
                "msgid": "live-msg-1",
            }
        )
        payload = build_text_send_payload(inbound, "我先站你这边。")

        self.assertEqual(inbound["channel"], "wecom_live")
        self.assertEqual(inbound["external_user_id"], "external-owner")
        self.assertEqual(inbound["open_kfid"], "wkf-123")
        self.assertEqual(inbound["content"], "老板又临下班改需求，真的离谱")
        self.assertEqual(payload["touser"], "external-owner")
        self.assertEqual(payload["open_kfid"], "wkf-123")
        self.assertEqual(payload["msgtype"], "text")
        self.assertEqual(payload["text"]["content"], "我先站你这边。")

    def test_wecom_live_dev_inbound_flow_uses_companion_and_send_payload(self):
        from app.server import create_wecom_live_dev_response, handle_wecom_live_callback_validation
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": "encrypted",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", "encrypted"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            callback = handle_wecom_live_callback_validation(config, query)
            response = create_wecom_live_dev_response(
                store,
                {
                    "external_userid": "external-owner",
                    "open_kfid": "wkf-123",
                    "msgtype": "text",
                    "text": {"content": "老板又临下班改需求，真的离谱"},
                    "msgid": "live-msg-2",
                },
            )

        self.assertEqual(callback["status"], "crypto_not_configured")
        self.assertEqual(response["inbound"]["channel"], "wecom_live")
        self.assertEqual(response["outbound_payload"]["touser"], "external-owner")
        self.assertIn("站你这边", response["outbound_payload"]["text"]["content"])


if __name__ == "__main__":
    unittest.main()
