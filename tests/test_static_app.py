import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticAppTests(unittest.TestCase):
    def test_static_app_contains_round_one_views_and_api_wiring(self):
        index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        for label in [
            "Chat Simulator",
            "Users",
            "Memory",
            "Sample Status",
            "Run Status",
        ]:
            self.assertIn(label, index)

        for endpoint in [
            "/api/status",
            "/api/users",
            "/api/chat",
            "/api/memories",
            "/api/sources",
        ]:
            self.assertIn(endpoint, script)

    def test_chat_bubbles_do_not_render_debug_metadata(self):
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn("<small>", script)
        self.assertNotIn("response.media.notice", script)


if __name__ == "__main__":
    unittest.main()
