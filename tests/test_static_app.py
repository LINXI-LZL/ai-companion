import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticAppTests(unittest.TestCase):
    def test_static_app_contains_round_one_views_and_api_wiring(self):
        index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        for label in [
            "聊天模拟",
            "用户",
            "记忆",
            "微信入口",
            "样本状态",
            "运行状态",
        ]:
            self.assertIn(label, index)

        for endpoint in [
            "/api/status",
            "/api/users",
            "/api/chat",
            "/api/wechat/mock-inbound",
            "/api/memories",
            "/api/sources",
        ]:
            self.assertIn(endpoint, script)

    def test_chat_bubbles_do_not_render_debug_metadata(self):
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn("<small>", script)
        self.assertNotIn("response.media.notice", script)

    def test_status_pages_render_human_readable_chinese_labels(self):
        index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        for label in ["来源", "授权", "下载策略", "流量", "服务", "素材状态"]:
            self.assertIn(label, index)

        for renderer in [
            "sourceStatusLabel(source.status)",
            "downloadPolicyLabel(source.download_policy)",
            "trafficLabel(source.traffic_level)",
            "assetTypeLabel(asset.asset_type)",
            "assetStatusLabel(asset.status)",
            "assetNoteLabel(asset.note)",
        ]:
            self.assertIn(renderer, script)

    def test_wechat_entry_contains_live_credential_self_check(self):
        index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn("真实接入自检", index)
        self.assertIn("wecom-live-status", index)
        self.assertIn("/api/wecom-live/status", script)
        self.assertIn("renderWecomLiveStatus", script)

    def test_memory_page_is_automatic_memory_manager(self):
        index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn("自动记忆", index)
        self.assertIn("智能体会从聊天里自动保存稳定偏好", index)
        self.assertIn("自动记忆为空", script)


if __name__ == "__main__":
    unittest.main()
