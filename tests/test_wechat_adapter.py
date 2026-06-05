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


if __name__ == "__main__":
    unittest.main()
