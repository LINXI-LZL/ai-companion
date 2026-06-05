# Build Round 1 Local Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local runnable companion simulator and admin foundation for the confirmed WeChat AI companion MVP.

**Architecture:** Use a modular monolith with Python standard-library HTTP routing, SQLite persistence, and static browser assets. Keep WeChat and real media behind stubs so the owner can test chat behavior before platform credentials, sticker rights, and voice providers are ready.

**Tech Stack:** Python 3.12 standard library (`http.server`, `sqlite3`, `unittest`), vanilla HTML/CSS/JavaScript, SQLite database file in `runtime/`.

---

## File Structure

| Path | Responsibility |
|---|---|
| `README.md` | Local run and test instructions |
| `app/__init__.py` | Package marker |
| `app/server.py` | Local HTTP server and API routes |
| `app/storage.py` | SQLite schema, seed data, and data access |
| `app/safety.py` | Safety-mode classification and safe reply text |
| `app/memory.py` | Lightweight preference memory extraction and controls |
| `app/multimodal.py` | Text/sticker/voice/safety mode decision |
| `app/media.py` | Media asset registry stub and fallback behavior |
| `app/orchestrator.py` | Personality response planning |
| `app/sample_sources.py` | Public-source status loader |
| `app/static/index.html` | Real local app UI |
| `app/static/styles.css` | Real local app styling |
| `app/static/app.js` | Real local app interactions |
| `tests/test_companion_core.py` | Unit tests for safety, memory, multimodal, and orchestration |
| `tests/test_storage_api.py` | Unit tests for storage and API route behavior |

## Success Criteria

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] `python -m app.server --port 8765` starts a local app.
- [ ] Browser can open `http://127.0.0.1:8765`.
- [ ] The simulator returns normal friend-like replies, safety replies, memory behavior, and sticker/voice intent fallback.
- [ ] Admin views show users, whitelist, memory, public sample status, and run status.
- [ ] `docs/project_state.json` moves to development progress with completed first-round steps.

## Task 1: Core Behavior Tests

**Files:**
- Create: `tests/test_companion_core.py`
- Create: `app/__init__.py`
- Create minimal modules only after RED is verified.

- [ ] **Step 1: Write failing tests**

```python
def test_high_risk_message_uses_safety_mode():
    from app.orchestrator import plan_reply
    plan = plan_reply("u1", "我真的撑不下去了，不想继续了", memories=[])
    assert plan["safety_mode"] is True
    assert plan["mode"] == "safety_response"
    assert plan["sticker_intent"] == "none"
    assert "先别一个人扛" in plan["reply_text"]

def test_low_risk_work_rant_uses_sticker_intent():
    from app.orchestrator import plan_reply
    plan = plan_reply("u1", "老板又临下班改需求，真的离谱", memories=[])
    assert plan["safety_mode"] is False
    assert plan["mode"] == "text_plus_sticker"
    assert plan["sticker_intent"] == "sticker_speechless"
    assert "离谱" in plan["reply_text"]

def test_late_night_tired_message_uses_voice_script():
    from app.orchestrator import plan_reply
    plan = plan_reply("u1", "今天好累，但睡不着", memories=[])
    assert plan["mode"] == "text_plus_short_voice"
    assert plan["voice_intent"] == "voice_sleepy_companion"
    assert plan["voice_script"]

def test_memory_can_be_reflected_in_reply():
    from app.orchestrator import plan_reply
    plan = plan_reply("u1", "今天又开始emo", memories=["用户喜欢短回复"])
    assert "我会短点说" in plan["reply_text"]
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_companion_core -v`

Expected: imports fail because `app.orchestrator` does not exist.

- [ ] **Step 3: Implement minimal core modules**

Create `app/safety.py`, `app/multimodal.py`, `app/media.py`, `app/orchestrator.py` with deterministic rules from `docs/behavior_distillation_rules.md`.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest tests.test_companion_core -v`

Expected: 4 tests pass.

## Task 2: SQLite Storage And Sample Sources

**Files:**
- Create: `tests/test_storage_api.py`
- Create: `app/storage.py`
- Create: `app/sample_sources.py`

- [ ] **Step 1: Write failing tests**

```python
def test_storage_initializes_users_memory_messages_and_sources(tmp_path):
    from app.storage import Storage
    store = Storage(tmp_path / "app.db")
    store.initialize()
    user = store.create_user("owner", "Owner", allowed=True)
    store.save_memory(user["id"], "用户喜欢短回复", source="manual")
    memories = store.list_memories(user["id"])
    assert memories[0]["content"] == "用户喜欢短回复"

def test_sample_sources_load_manifest_statuses():
    from app.sample_sources import load_source_status
    sources = load_source_status()
    assert any(source["id"] == "source-cped" for source in sources)
    assert all("download_policy" in source for source in sources)
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_storage_api -v`

Expected: imports fail because storage modules do not exist.

- [ ] **Step 3: Implement storage and source loader**

Create SQLite tables for users, memories, messages, audit_events, and media_assets. Load source status from `data/public_sources/data_sources.json`.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest tests.test_storage_api -v`

Expected: storage tests pass.

## Task 3: HTTP API And Static App

**Files:**
- Modify: `app/server.py`
- Create: `app/static/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`

- [ ] **Step 1: Add API tests**

Extend `tests/test_storage_api.py` to exercise route handlers without starting a browser:

```python
def test_app_core_chat_response_persists_message(tmp_path):
    from app.storage import Storage
    from app.server import create_chat_response
    store = Storage(tmp_path / "app.db")
    store.initialize()
    user = store.create_user("owner", "Owner", allowed=True)
    response = create_chat_response(store, {"user_id": user["id"], "message": "我又拖到最后一天，真服了"})
    assert response["plan"]["mode"] == "text_plus_sticker"
    assert response["media"]["fallback_to_text"] is True
    assert len(store.list_messages(user["id"])) == 1
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_storage_api -v`

Expected: `create_chat_response` missing.

- [ ] **Step 3: Implement API/server**

Implement `GET /api/status`, `GET/POST /api/users`, `GET /api/sources`, `GET/POST/DELETE /api/memories`, and `POST /api/chat`.

- [ ] **Step 4: Implement static UI**

Build admin tabs for Chat Simulator, Users, Memory, Sample Status, and Run Status. Wire API calls with `fetch`.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

## Task 4: Project State And Verification

**Files:**
- Modify: `docs/project_state.json`
- Modify: `docs/progress_board.md`
- Modify: `docs/master_task_board.md`
- Modify: `docs/artifact_registry.md`
- Modify: `docs/decision_log.md`

- [ ] **Step 1: Mark Build Round 1 scope confirmed**

Set `decision-009` to `resolved`, mark `step-06-01-build-scope-round-1` done, and move current position into `phase-07-development`.

- [ ] **Step 2: Mark completed implementation steps**

After verification, mark completed steps from `step-07-01-project-scaffold` through the last implemented first-round step.

- [ ] **Step 3: Verify project state**

Run JSON parse and phase-count checks against `docs/project_state.json`.

- [ ] **Step 4: Commit**

Commit implementation and state updates with a concise message.
