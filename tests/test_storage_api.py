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


if __name__ == "__main__":
    unittest.main()
