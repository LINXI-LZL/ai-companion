import argparse
import json
import mimetypes
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .auto_memory import can_store_memory, infer_auto_memories
from .llm_router import load_router_config_from_env, route_external_reply
from .orchestrator import plan_reply
from .sample_sources import load_source_status
from .storage import DEFAULT_DB, Storage
from .wecom_live import (
    build_text_send_payload,
    handle_callback_validation,
    load_wecom_config_from_env,
    normalize_live_event,
)
from .wechat_adapter import build_outbound_message, normalize_inbound_event, resolve_mock_user


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"


def create_chat_response(store, payload, router_config=None, router_transport=None):
    user_id = payload.get("user_id") or ""
    message = (payload.get("message") or "").strip()
    if not message:
        raise ValueError("message is required")

    user = store.get_user(user_id)
    if not user:
        raise ValueError("user not found")
    if not user["allowed"]:
        raise PermissionError("user is not allowlisted")

    recent_messages = store.list_messages(user_id, limit=None)
    extracted_memory = _extract_memory(message)
    if extracted_memory:
        _save_memory_once(store, user_id, extracted_memory, source="chat")
    for memory in infer_auto_memories(message, recent_messages):
        _save_memory_once(store, user_id, memory, source="auto")

    memories = [memory["content"] for memory in store.list_memories(user_id)]
    plan = plan_reply(user_id, message, memories=memories, recent_messages=recent_messages)
    router_config = router_config or load_router_config_from_env(os.environ)
    routed = route_external_reply(
        router_config,
        plan,
        message,
        memories=memories,
        recent_messages=recent_messages,
        transport=router_transport,
    )
    _apply_router_result(plan, routed)
    saved = store.save_message(user_id, message, plan)
    store.record_audit(
        "chat_response",
        {
            "user_id": user_id,
            "message_id": saved["id"],
            "mode": plan["mode"],
            "safety_mode": plan["safety_mode"],
            "llm_provider": plan["llm"]["provider"],
            "llm_fallback_reason": plan["llm"]["fallback_reason"],
        },
    )
    return {
        "message": saved,
        "plan": plan,
        "media": plan["media"],
        "memories": store.list_memories(user_id),
    }


def create_mock_wechat_response(store, payload):
    inbound = normalize_inbound_event(payload)
    user = resolve_mock_user(store, inbound)
    chat = create_chat_response(store, {"user_id": user["id"], "message": inbound["content"]})
    outbound = build_outbound_message(inbound, chat["plan"])
    return {
        "inbound": inbound,
        "user": user,
        "chat": chat,
        "outbound": outbound,
    }


def handle_wecom_live_callback_validation(config, query):
    return handle_callback_validation(config, query)


def create_wecom_live_dev_response(store, payload):
    inbound = normalize_live_event(payload)
    user = resolve_mock_user(store, {"external_user_id": inbound["external_user_id"]})
    chat = create_chat_response(store, {"user_id": user["id"], "message": inbound["content"]})
    outbound_payload = build_text_send_payload(inbound, chat["plan"]["reply_text"])
    store.record_audit(
        "wecom_live_dev_response",
        {
            "user_id": user["id"],
            "external_user_id": inbound["external_user_id"],
            "open_kfid": inbound["open_kfid"],
            "mode": chat["plan"]["mode"],
        },
    )
    return {
        "inbound": inbound,
        "user": user,
        "chat": chat,
        "outbound_payload": outbound_payload,
        "send_policy": "payload_only",
    }


def _extract_memory(message):
    text = message.strip()
    prefixes = ("记住：", "记住:", "帮我记住", "你记一下")
    for prefix in prefixes:
        if text.startswith(prefix):
            content = text[len(prefix) :].strip(" ，,。")
            return content or None
    if "我喜欢短回复" in text:
        return "用户喜欢短回复"
    return None


def _save_memory_once(store, user_id, content, source):
    if not can_store_memory(content):
        return None
    existing = {memory["content"] for memory in store.list_memories(user_id)}
    if content in existing:
        return None
    return store.save_memory(user_id, content, source=source)


def _apply_router_result(plan, routed):
    plan["llm"] = routed["metadata"]
    if routed["reply_text"] == plan["reply_text"]:
        return
    plan["reply_text"] = routed["reply_text"]
    plan["voice_script"] = _build_voice_script(plan["reply_text"], plan["voice_intent"])


def _build_voice_script(reply_text, voice_intent):
    if voice_intent == "voice_sleepy_companion":
        return "低一点声音说：" + reply_text
    if voice_intent == "voice_serious_grounding":
        return "认真平稳地说：" + reply_text
    return ""


class CompanionRequestHandler(SimpleHTTPRequestHandler):
    store = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json(
                {
                    "status": "ok",
                    "app": "微信树洞 AI local companion",
                    "database": str(self.store.db_path),
                }
            )
            return
        if parsed.path == "/api/users":
            self._send_json({"users": self.store.list_users()})
            return
        if parsed.path == "/api/sources":
            self._send_json({"sources": load_source_status()})
            return
        if parsed.path == "/api/media":
            self._send_json({"assets": self.store.list_media_assets()})
            return
        if parsed.path == "/api/wecom-live/status":
            self._send_json({"status": load_wecom_config_from_env(os.environ).to_status()})
            return
        if parsed.path == "/api/llm-router/status":
            self._send_json({"status": load_router_config_from_env(os.environ).to_status()})
            return
        if parsed.path == "/api/wecom-live/callback":
            query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
            result = handle_wecom_live_callback_validation(load_wecom_config_from_env(os.environ), query)
            if result.get("reply_text"):
                self._send_text(result["reply_text"], status=result["http_status"])
            else:
                self._send_json(result, status=result["http_status"])
            return
        if parsed.path == "/api/memories":
            user_id = parse_qs(parsed.query).get("user_id", [None])[0]
            self._send_json({"memories": self.store.list_memories(user_id)})
            return
        if parsed.path == "/api/messages":
            user_id = parse_qs(parsed.query).get("user_id", [None])[0]
            self._send_json({"messages": self.store.list_messages(user_id)})
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/users":
                user = self.store.create_user(
                    payload.get("handle", "").strip(),
                    payload.get("display_name", "").strip() or payload.get("handle", "").strip(),
                    allowed=bool(payload.get("allowed", True)),
                )
                self._send_json({"user": user}, status=201)
                return
            if parsed.path == "/api/memories":
                memory = self.store.save_memory(
                    payload.get("user_id", ""),
                    payload.get("content", "").strip(),
                    source=payload.get("source", "manual"),
                )
                self._send_json({"memory": memory}, status=201)
                return
            if parsed.path == "/api/chat":
                self._send_json(create_chat_response(self.store, payload), status=201)
                return
            if parsed.path == "/api/wechat/mock-inbound":
                self._send_json(create_mock_wechat_response(self.store, payload), status=201)
                return
            if parsed.path == "/api/wecom-live/dev-inbound":
                self._send_json(create_wecom_live_dev_response(self.store, payload), status=201)
                return
            self._send_json({"error": "not found"}, status=404)
        except PermissionError as exc:
            self._send_json({"error": str(exc)}, status=403)
        except (ValueError, KeyError) as exc:
            self._send_json({"error": str(exc)}, status=400)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/users/"):
            user_id = parsed.path.rsplit("/", 1)[-1]
            payload = self._read_json()
            user = self.store.set_user_allowed(user_id, bool(payload.get("allowed")))
            if user:
                self._send_json({"user": user})
            else:
                self._send_json({"error": "user not found"}, status=404)
            return
        self._send_json({"error": "not found"}, status=404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/memories":
            user_id = parse_qs(parsed.query).get("user_id", [None])[0]
            if not user_id:
                self._send_json({"error": "user_id is required"}, status=400)
                return
            self.store.clear_memories(user_id)
            self._send_json({"ok": True})
            return
        self._send_json({"error": "not found"}, status=404)

    def _serve_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        target = (STATIC_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists():
            self._send_json({"error": "not found"}, status=404)
            return
        content = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text, status=200):
        body = str(text).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def make_server(port=8765, db_path=DEFAULT_DB):
    store = Storage(db_path)
    store.initialize()
    handler = type("RuntimeCompanionRequestHandler", (CompanionRequestHandler,), {"store": store})
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


def main():
    parser = argparse.ArgumentParser(description="Run the local companion simulator.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    server = make_server(args.port, Path(args.db))
    try:
        if sys.stdout:
            print(f"Local companion app running at http://127.0.0.1:{args.port}")
    except (OSError, ValueError):
        pass
    server.serve_forever()


if __name__ == "__main__":
    main()
