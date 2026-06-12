import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "runtime" / "companion.db"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, db_path=DEFAULT_DB):
        self.db_path = Path(db_path)

    def initialize(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    handle TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    allowed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    incoming_text TEXT NOT NULL,
                    reply_text TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    safety_mode INTEGER NOT NULL,
                    sticker_intent TEXT NOT NULL,
                    voice_intent TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS wecom_callback_jobs (
                    id TEXT PRIMARY KEY,
                    dedupe_key TEXT NOT NULL UNIQUE,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT NOT NULL DEFAULT '{}',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT NOT NULL DEFAULT '',
                    finished_at TEXT NOT NULL DEFAULT ''
                );

                CREATE INDEX IF NOT EXISTS idx_wecom_callback_jobs_status_created
                ON wecom_callback_jobs(status, created_at);

                CREATE TABLE IF NOT EXISTS wecom_processed_messages (
                    dedupe_key TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS media_assets (
                    id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    status TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._seed_media_assets(conn)
            now = utc_now()
            conn.execute(
                """
                INSERT OR IGNORE INTO users
                (id, handle, display_name, allowed, created_at, updated_at)
                VALUES ('user-owner', 'owner', 'Owner', 1, ?, ?)
                """,
                (now, now),
            )

    def create_user(self, handle, display_name, allowed=False):
        now = utc_now()
        user_id = f"user-{uuid.uuid4().hex[:12]}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (id, handle, display_name, allowed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(handle) DO UPDATE SET
                    display_name = excluded.display_name,
                    allowed = excluded.allowed,
                    updated_at = excluded.updated_at
                """,
                (user_id, handle, display_name, int(bool(allowed)), now, now),
            )
        return self.get_user_by_handle(handle)

    def list_users(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM users ORDER BY created_at ASC"
            ).fetchall()
        return [self._row_to_user(row) for row in rows]

    def get_user(self, user_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_handle(self, handle):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE handle = ?", (handle,)).fetchone()
        return self._row_to_user(row) if row else None

    def set_user_allowed(self, user_id, allowed):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET allowed = ?, updated_at = ? WHERE id = ?",
                (int(bool(allowed)), utc_now(), user_id),
            )
        return self.get_user(user_id)

    def save_memory(self, user_id, content, source="manual"):
        memory_id = f"mem-{uuid.uuid4().hex[:12]}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, content, source, enabled, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (memory_id, user_id, content, source, utc_now()),
            )
        return self.get_memory(memory_id)

    def get_memory(self, memory_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        return self._row_to_memory(row) if row else None

    def list_memories(self, user_id=None, enabled_only=True):
        where = []
        params = []
        if user_id:
            where.append("user_id = ?")
            params.append(user_id)
        if enabled_only:
            where.append("enabled = 1")
        query = "SELECT * FROM memories"
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def clear_memories(self, user_id):
        with self._connect() as conn:
            conn.execute("UPDATE memories SET enabled = 0 WHERE user_id = ?", (user_id,))

    def save_message(self, user_id, incoming_text, plan):
        message_id = f"msg-{uuid.uuid4().hex[:12]}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages
                (id, user_id, incoming_text, reply_text, mode, safety_mode, sticker_intent,
                 voice_intent, plan_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    user_id,
                    incoming_text,
                    plan["reply_text"],
                    plan["mode"],
                    int(bool(plan["safety_mode"])),
                    plan["sticker_intent"],
                    plan["voice_intent"],
                    json.dumps(plan, ensure_ascii=False),
                    utc_now(),
                ),
            )
        return self.get_message(message_id)

    def get_message(self, message_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
        return self._row_to_message(row) if row else None

    def list_messages(self, user_id=None, limit=30):
        params = []
        query = "SELECT * FROM messages"
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        query += " ORDER BY created_at DESC, rowid DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_message(row) for row in rows]

    def record_audit(self, event_type, payload):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_events (id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    f"audit-{uuid.uuid4().hex[:12]}",
                    event_type,
                    json.dumps(payload, ensure_ascii=False),
                    utc_now(),
                ),
            )

    def list_audit_events(self, limit=30):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events ORDER BY created_at DESC, rowid DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_audit_event(row) for row in rows]

    def enqueue_wecom_callback_job(self, dedupe_key, job_type, payload):
        now = utc_now()
        job_id = f"wecom-job-{uuid.uuid4().hex[:12]}"
        payload_json = json.dumps(payload, ensure_ascii=False)
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO wecom_callback_jobs
                (id, dedupe_key, job_type, status, payload_json, result_json, attempts,
                 last_error, created_at, updated_at, started_at, finished_at)
                VALUES (?, ?, ?, 'queued', ?, '{}', 0, '', ?, ?, '', '')
                """,
                (job_id, dedupe_key, job_type, payload_json, now, now),
            )
            created = cursor.rowcount == 1
            if created:
                row = conn.execute("SELECT * FROM wecom_callback_jobs WHERE id = ?", (job_id,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM wecom_callback_jobs WHERE dedupe_key = ?", (dedupe_key,)).fetchone()
        return self._row_to_wecom_callback_job(row), created

    def list_wecom_callback_jobs(self, status=None, limit=30):
        params = []
        query = "SELECT * FROM wecom_callback_jobs"
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at ASC, rowid ASC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_wecom_callback_job(row) for row in rows]

    def claim_next_wecom_callback_job(self):
        now = utc_now()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """
                SELECT * FROM wecom_callback_jobs
                WHERE status = 'queued'
                ORDER BY created_at ASC, rowid ASC
                LIMIT 1
                """
            ).fetchone()
            if not row:
                return None
            conn.execute(
                """
                UPDATE wecom_callback_jobs
                SET status = 'running', attempts = attempts + 1, updated_at = ?, started_at = ?
                WHERE id = ?
                """,
                (now, now, row["id"]),
            )
            claimed = conn.execute("SELECT * FROM wecom_callback_jobs WHERE id = ?", (row["id"],)).fetchone()
        return self._row_to_wecom_callback_job(claimed)

    def finish_wecom_callback_job(self, job_id, result):
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE wecom_callback_jobs
                SET status = 'done', result_json = ?, updated_at = ?, finished_at = ?, last_error = ''
                WHERE id = ?
                """,
                (json.dumps(result, ensure_ascii=False), now, now, job_id),
            )
        return self.get_wecom_callback_job(job_id)

    def fail_wecom_callback_job(self, job_id, reason):
        now = utc_now()
        safe_reason = str(reason or "")[:240]
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE wecom_callback_jobs
                SET status = 'failed', last_error = ?, updated_at = ?, finished_at = ?
                WHERE id = ?
                """,
                (safe_reason, now, now, job_id),
            )
        return self.get_wecom_callback_job(job_id)

    def get_wecom_callback_job(self, job_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM wecom_callback_jobs WHERE id = ?", (job_id,)).fetchone()
        return self._row_to_wecom_callback_job(row) if row else None

    def mark_wecom_message_processed(self, dedupe_key, payload):
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO wecom_processed_messages
                (dedupe_key, payload_json, created_at)
                VALUES (?, ?, ?)
                """,
                (dedupe_key, json.dumps(payload, ensure_ascii=False), utc_now()),
            )
        return cursor.rowcount == 1

    def list_media_assets(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM media_assets ORDER BY intent ASC").fetchall()
        return [dict(row) for row in rows]

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _seed_media_assets(self, conn):
        now = utc_now()
        defaults = [
            ("asset-sticker-speechless", "sticker", "sticker_speechless", "deferred", "Real sticker files wait for rights review."),
            ("asset-sticker-hug", "sticker", "sticker_supportive_hug", "deferred", "Use text fallback for now."),
            ("asset-voice-sleepy", "voice", "voice_sleepy_companion", "deferred", "Voice provider is not chosen yet."),
        ]
        for item in defaults:
            conn.execute(
                """
                INSERT OR IGNORE INTO media_assets
                (id, asset_type, intent, status, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (*item, now),
            )

    @staticmethod
    def _row_to_user(row):
        return {
            "id": row["id"],
            "handle": row["handle"],
            "display_name": row["display_name"],
            "allowed": bool(row["allowed"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    @staticmethod
    def _row_to_memory(row):
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "content": row["content"],
            "source": row["source"],
            "enabled": bool(row["enabled"]),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _row_to_message(row):
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "incoming_text": row["incoming_text"],
            "reply_text": row["reply_text"],
            "mode": row["mode"],
            "safety_mode": bool(row["safety_mode"]),
            "sticker_intent": row["sticker_intent"],
            "voice_intent": row["voice_intent"],
            "plan": json.loads(row["plan_json"]),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _row_to_audit_event(row):
        return {
            "id": row["id"],
            "event_type": row["event_type"],
            "payload": json.loads(row["payload_json"]),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _row_to_wecom_callback_job(row):
        return {
            "id": row["id"],
            "dedupe_key": row["dedupe_key"],
            "job_type": row["job_type"],
            "status": row["status"],
            "payload": json.loads(row["payload_json"]),
            "result": json.loads(row["result_json"] or "{}"),
            "attempts": row["attempts"],
            "last_error": row["last_error"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
        }
