import argparse
import hashlib
import json
import mimetypes
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .auto_memory import can_store_memory, infer_auto_memories
from .wecom_kf_api import WeComKfApiError, send_kf_text_message, sync_kf_text_messages
from .llm_router import load_router_config_from_env, route_external_reply
from .orchestrator import avoid_recent_reply_repeat, plan_reply
from .sample_sources import load_source_status
from .storage import DEFAULT_DB, Storage
from .wecom_live import (
    build_text_send_payload,
    decrypt_encrypted_callback_event,
    handle_callback_validation,
    load_wecom_config_from_env,
    normalize_live_event,
)
from .wechat_adapter import build_outbound_message, normalize_inbound_event, resolve_mock_user


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"
AUTO_MEMORY_BACKFILL_LIMIT = 12
WECOM_WORKER_POLL_SECONDS = 0.8


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
    for memory in _infer_recent_auto_memories(recent_messages):
        _save_memory_once(store, user_id, memory, source="auto")
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
        user_id=user_id,
    )
    _apply_router_result(plan, routed)
    avoid_recent_reply_repeat(plan, recent_messages)
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


def create_wecom_live_callback_response(store, config, query, body, sync_transport=None, send_transport=None):
    event = decrypt_encrypted_callback_event(config, query, body)
    if event["status"] != "ok":
        store.record_audit(
            "wecom_live_callback_failure",
            _build_wecom_callback_audit_payload(event, body),
        )
        return event
    inbound = event["inbound"]
    job_type = "direct_text" if inbound["content"] else "sync_event"
    dedupe_key = _build_wecom_callback_dedupe_key(inbound)
    job, created = store.enqueue_wecom_callback_job(
        dedupe_key,
        job_type,
        {
            "inbound": inbound,
            "status": event["status"],
            "signature_valid": bool(event["signature_valid"]),
            "body_has_encrypt": bool(event["body_has_encrypt"]),
        },
    )
    if not created:
        store.record_audit(
            "wecom_live_callback_duplicate",
            _build_wecom_job_audit_payload(job, inbound, status="duplicate"),
        )
        return {
            **event,
            "status": "duplicate",
            "job_id": job["id"],
            "job_status": job["status"],
            "ack_text": "success",
        }
    store.record_audit(
        "wecom_live_callback_queued",
        _build_wecom_job_audit_payload(job, inbound, status="queued"),
    )
    return {
        **event,
        "status": "queued",
        "job_id": job["id"],
        "job_status": job["status"],
        "ack_text": "success",
    }


def process_next_wecom_live_job(store, config, sync_transport=None, send_transport=None):
    job = store.claim_next_wecom_callback_job()
    if not job:
        return {"status": "idle"}
    inbound = job["payload"].get("inbound", {})
    store.record_audit(
        "wecom_live_job_started",
        _build_wecom_job_audit_payload(job, inbound, status="running"),
    )
    try:
        if job["job_type"] == "sync_event":
            result = _handle_wecom_sync_event(store, config, {"inbound": inbound}, inbound, sync_transport, send_transport)
        else:
            result = _handle_wecom_direct_text_job(store, config, inbound, send_transport or sync_transport)
        store.finish_wecom_callback_job(job["id"], _build_wecom_job_result(result))
        store.record_audit(
            "wecom_live_job_done",
            _build_wecom_job_done_audit_payload(job, inbound, result),
        )
        return {"status": "done", "job_id": job["id"], "result": result}
    except Exception as exc:
        store.fail_wecom_callback_job(job["id"], exc.__class__.__name__)
        store.record_audit(
            "wecom_live_job_failed",
            {
                **_build_wecom_job_audit_payload(job, inbound, status="failed"),
                "reason": exc.__class__.__name__,
            },
        )
        return {"status": "failed", "job_id": job["id"], "reason": exc.__class__.__name__}


def _handle_wecom_direct_text_job(store, config, inbound, transport=None):
    message_key = _build_wecom_message_dedupe_key(inbound)
    if message_key and not store.mark_wecom_message_processed(message_key, _build_wecom_message_seen_payload(inbound)):
        store.record_audit(
            "wecom_live_message_duplicate",
            _build_wecom_message_duplicate_payload(inbound),
        )
        return {
            "status": "message_duplicate",
            "send_policy": "ack_only",
            "processed_count": 0,
            "sent_count": 0,
        }
    user = resolve_mock_user(store, {"external_user_id": inbound["external_user_id"]})
    chat = create_chat_response(store, {"user_id": user["id"], "message": inbound["content"]})
    outbound_payload = build_text_send_payload(inbound, chat["plan"]["reply_text"])
    send_result = _send_wecom_text_payload(store, config, outbound_payload, transport)
    store.record_audit(
        "wecom_live_callback_response",
        {
            "user_id": user["id"],
            "external_user_id": inbound["external_user_id"],
            "open_kfid": inbound["open_kfid"],
            "mode": chat["plan"]["mode"],
            "send_policy": send_result["send_policy"],
        },
    )
    return {
        "user": user,
        "chat": chat,
        "outbound_payload": outbound_payload,
        "send_policy": send_result["send_policy"],
        "send_result": send_result["send_result"],
        "processed_count": 1,
        "sent_count": 1 if send_result["send_policy"] == "real_text_send" else 0,
    }


def _handle_wecom_sync_event(store, config, event, inbound, sync_transport=None, send_transport=None):
    try:
        sync_response = sync_kf_text_messages(
            config,
            inbound["message_token"],
            open_kfid=inbound["open_kfid"],
            transport=sync_transport,
        )
    except WeComKfApiError as exc:
        audit_type = "wecom_live_sync_msg_deferred" if exc.code == "missing_sync_config" else "wecom_live_sync_msg_failure"
        store.record_audit(
            audit_type,
            {
                "status": "sync_msg_deferred" if exc.code == "missing_sync_config" else "sync_msg_failed",
                "reason": exc.code,
                "content_type": inbound["content_type"],
                "event": inbound["event"],
                "open_kfid": inbound["open_kfid"],
                "message_token_present": bool(inbound["message_token"]),
            },
        )
        return {
            **event,
            "status": "sync_msg_deferred" if exc.code == "missing_sync_config" else "sync_msg_failed",
            "ack_text": "success",
            "send_policy": "ack_only",
        }

    processed = []
    for message in sync_response.get("msg_list", []):
        synced_inbound = normalize_live_event(message)
        if synced_inbound["content_type"] != "text" or not synced_inbound["content"]:
            continue
        message_key = _build_wecom_message_dedupe_key(synced_inbound)
        if message_key and not store.mark_wecom_message_processed(message_key, _build_wecom_message_seen_payload(synced_inbound)):
            store.record_audit(
                "wecom_live_message_duplicate",
                _build_wecom_message_duplicate_payload(synced_inbound),
            )
            continue
        user = resolve_mock_user(store, {"external_user_id": synced_inbound["external_user_id"]})
        chat = create_chat_response(store, {"user_id": user["id"], "message": synced_inbound["content"]})
        outbound_payload = build_text_send_payload(synced_inbound, chat["plan"]["reply_text"])
        send_result = _send_wecom_text_payload(store, config, outbound_payload, send_transport or sync_transport)
        processed.append(
            {
                "inbound": synced_inbound,
                "user": user,
                "chat": chat,
                "outbound_payload": outbound_payload,
                "send_result": send_result["send_result"],
                "send_policy": send_result["send_policy"],
            }
        )

    sent_count = sum(1 for item in processed if item["send_policy"] == "real_text_send")
    store.record_audit(
        "wecom_live_sync_msg_processed",
        {
            "status": "sync_msg_processed",
            "processed_count": len(processed),
            "sent_count": sent_count,
            "received_count": len(sync_response.get("msg_list", [])),
            "has_more": bool(sync_response.get("has_more")),
            "next_cursor_present": bool(sync_response.get("next_cursor")),
            "open_kfid": inbound["open_kfid"],
        },
    )
    return {
        **event,
        "status": "sync_msg_processed",
        "ack_text": "success",
        "send_policy": _resolve_batch_send_policy(processed, sent_count),
        "processed_count": len(processed),
        "received_count": len(sync_response.get("msg_list", [])),
        "outbound_payloads": [item["outbound_payload"] for item in processed],
        "send_results": [item["send_result"] for item in processed],
    }


def _build_wecom_callback_dedupe_key(inbound):
    open_kfid = inbound.get("open_kfid") or "-"
    if inbound.get("source_message_id"):
        return f"direct:{open_kfid}:{inbound['source_message_id']}"
    if inbound.get("message_token"):
        return f"sync:{open_kfid}:{inbound.get('event') or '-'}:{inbound['message_token']}"
    fallback = "|".join(
        [
            inbound.get("external_user_id", ""),
            open_kfid,
            inbound.get("content_type", ""),
            inbound.get("event", ""),
            inbound.get("content", ""),
        ]
    )
    return "fallback:" + hashlib.sha256(fallback.encode("utf-8")).hexdigest()


def _build_wecom_message_dedupe_key(inbound):
    source_message_id = inbound.get("source_message_id") or ""
    if not source_message_id:
        return ""
    return f"message:{inbound.get('open_kfid') or '-'}:{source_message_id}"


def _build_wecom_message_seen_payload(inbound):
    return {
        "open_kfid": inbound.get("open_kfid", ""),
        "external_user_id": inbound.get("external_user_id", ""),
        "source_message_id_present": bool(inbound.get("source_message_id")),
        "content_type": inbound.get("content_type", ""),
    }


def _build_wecom_message_duplicate_payload(inbound):
    return {
        "status": "message_duplicate",
        "open_kfid": inbound.get("open_kfid", ""),
        "external_user_id": inbound.get("external_user_id", ""),
        "source_message_id_present": bool(inbound.get("source_message_id")),
        "content_type": inbound.get("content_type", ""),
    }


def _build_wecom_job_audit_payload(job, inbound, status):
    return {
        "status": status,
        "job_id": job.get("id", ""),
        "job_type": job.get("job_type", ""),
        "dedupe_fingerprint": _fingerprint(job.get("dedupe_key", "")),
        "open_kfid": inbound.get("open_kfid", ""),
        "content_type": inbound.get("content_type", ""),
        "event": inbound.get("event", ""),
        "has_content": bool(inbound.get("content")),
        "source_message_id_present": bool(inbound.get("source_message_id")),
        "message_token_present": bool(inbound.get("message_token")),
    }


def _build_wecom_job_done_audit_payload(job, inbound, result):
    return {
        **_build_wecom_job_audit_payload(job, inbound, status="done"),
        "result_status": result.get("status", ""),
        "send_policy": result.get("send_policy", ""),
        "processed_count": result.get("processed_count", 0),
        "sent_count": result.get("sent_count", 0),
    }


def _build_wecom_job_result(result):
    return {
        "status": result.get("status", "processed"),
        "send_policy": result.get("send_policy", ""),
        "processed_count": result.get("processed_count", 0),
        "sent_count": result.get("sent_count", 0),
    }


def _fingerprint(value):
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _send_wecom_text_payload(store, config, outbound_payload, transport=None):
    try:
        response = send_kf_text_message(config, outbound_payload, transport=transport)
    except WeComKfApiError as exc:
        status = "send_msg_deferred" if exc.code == "missing_send_config" else "send_msg_failed"
        store.record_audit(
            "wecom_live_send_msg_failure",
            {
                "status": status,
                "reason": exc.code,
                "touser_present": bool((outbound_payload or {}).get("touser")),
                "open_kfid": (outbound_payload or {}).get("open_kfid", ""),
                "msgtype": (outbound_payload or {}).get("msgtype", ""),
            },
        )
        return {
            "send_policy": "payload_only",
            "send_result": {
                "status": status,
                "reason": exc.code,
            },
        }

    msgid = response.get("msgid") or response.get("msg_id") or ""
    store.record_audit(
        "wecom_live_send_msg_success",
        {
            "status": "sent",
            "errcode": response.get("errcode", 0),
            "msgid_present": bool(msgid),
            "touser_present": bool((outbound_payload or {}).get("touser")),
            "open_kfid": (outbound_payload or {}).get("open_kfid", ""),
            "msgtype": (outbound_payload or {}).get("msgtype", ""),
        },
    )
    return {
        "send_policy": "real_text_send",
        "send_result": {
            "status": "sent",
            "msgid": msgid,
        },
    }


def _resolve_batch_send_policy(processed, sent_count):
    if not processed:
        return "ack_only"
    if sent_count == len(processed):
        return "real_text_send"
    if sent_count:
        return "partial_text_send"
    return "payload_only"


def _build_wecom_callback_audit_payload(event, body):
    return {
        "status": event.get("status"),
        "http_status": event.get("http_status"),
        "signature_valid": bool(event.get("signature_valid")),
        "body_has_encrypt": bool(event.get("body_has_encrypt")),
        "body_length": len(body or ""),
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


def _infer_recent_auto_memories(recent_messages):
    memories = []
    for item in reversed(list(recent_messages)[:AUTO_MEMORY_BACKFILL_LIMIT]):
        for memory in infer_auto_memories(item.get("incoming_text", ""), []):
            if memory not in memories:
                memories.append(memory)
    return memories


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
            if parsed.path == "/api/wecom-live/callback":
                query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
                result = create_wecom_live_callback_response(
                    self.store,
                    load_wecom_config_from_env(os.environ),
                    query,
                    self._read_text(),
                )
                if result.get("ack_text"):
                    self._send_text(result["ack_text"], status=200)
                else:
                    self._send_json(result, status=result.get("http_status", 400))
                return
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

    def _read_text(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return ""
        return self.rfile.read(length).decode("utf-8")

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


class WeComLiveBackgroundWorker:
    def __init__(self, store, config_loader, poll_seconds=WECOM_WORKER_POLL_SECONDS):
        self.store = store
        self.config_loader = config_loader
        self.poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="wecom-live-worker", daemon=True)

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            result = process_next_wecom_live_job(self.store, self.config_loader())
            if result["status"] == "idle":
                self._stop.wait(self.poll_seconds)
            else:
                time.sleep(0)


def make_server(port=8765, db_path=DEFAULT_DB):
    store = Storage(db_path)
    store.initialize()
    handler = type("RuntimeCompanionRequestHandler", (CompanionRequestHandler,), {"store": store})
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server.wecom_worker = WeComLiveBackgroundWorker(store, lambda: load_wecom_config_from_env(os.environ))
    server.wecom_worker.start()
    return server


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
