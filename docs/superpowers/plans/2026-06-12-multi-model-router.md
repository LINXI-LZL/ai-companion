# Multi-Model Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an external model router that can use OpenAI, DeepSeek, or Gemini as the companion's reply brain while preserving local fallback behavior.

**Architecture:** Keep `app/orchestrator.py` as the local planner and fallback. Add `app/llm_router.py` as a provider-neutral router that loads environment configuration, builds prompts, calls providers through a replaceable transport, and returns a reply candidate plus metadata. Wire it through `app/server.py` after local planning and expose redacted router status to the admin UI.

**Tech Stack:** Python standard library (`os`, `json`, `urllib.request`, `time`), existing `unittest` suite, existing static HTML/CSS/JS admin console.

---

### Task 1: Router Core

**Files:**
- Create: `app/llm_router.py`
- Test: `tests/test_llm_router.py`

- [x] **Step 1: Write failing router config and fallback tests**

Create tests that assert:

```python
from app.llm_router import load_router_config_from_env, route_external_reply

def test_router_defaults_to_local_without_keys():
    config = load_router_config_from_env({})
    assert config.to_status()["enabled"] is False
    result = route_external_reply(config, {"reply_text": "local"}, "你好", [], [], transport=lambda request: "remote")
    assert result["reply_text"] == "local"
    assert result["metadata"]["provider"] == "local"
    assert result["metadata"]["fallback_reason"] == "router_disabled"
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_llm_router -v`
Expected: import failure for `app.llm_router`.

- [x] **Step 3: Implement minimal config, status, prompt, and routing**

Create `RouterConfig`, `ProviderConfig`, `load_router_config_from_env`, `route_external_reply`, and `build_prompt_messages`. Use no third-party dependency.

- [x] **Step 4: Run router tests**

Run: `python -m unittest tests.test_llm_router -v`
Expected: router tests pass.

### Task 2: Server Integration

**Files:**
- Modify: `app/server.py`
- Test: `tests/test_storage_api.py`

- [x] **Step 1: Write failing chat integration tests**

Add tests that pass a fake router transport into `create_chat_response` and assert:

```python
response["plan"]["reply_text"] == "外部模型回复"
response["plan"]["llm"]["provider"] == "openai"
```

Also assert high-risk messages keep the local safety reply and do not call the external transport.

- [x] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.test_storage_api -v`
Expected: `create_chat_response` does not accept router injection or does not attach `llm` metadata.

- [x] **Step 3: Wire router after local plan**

Update `create_chat_response(store, payload, router_config=None, router_transport=None)`:

1. Create local plan first.
2. Call router only for non-safety plans.
3. If router returns an external reply, replace `plan["reply_text"]`.
4. Rebuild `voice_script` only if needed later; first scope only updates text reply.
5. Save `plan["llm"]` metadata.
6. Include provider metadata in audit.

- [x] **Step 4: Run storage/API tests**

Run: `python -m unittest tests.test_storage_api -v`
Expected: storage/API tests pass.

### Task 3: Admin Status UI

**Files:**
- Modify: `app/server.py`
- Modify: `app/static/index.html`
- Modify: `app/static/app.js`
- Modify: `app/static/styles.css`
- Test: `tests/test_static_app.py`

- [x] **Step 1: Write failing static/status tests**

Assert the UI contains `外部主脑`, calls `/api/llm-router/status`, and renders provider fields without secret values.

- [x] **Step 2: Run tests to verify failure**

Run: `python -m unittest tests.test_static_app -v`
Expected: missing router status UI/API references.

- [x] **Step 3: Add `/api/llm-router/status` and UI panel**

Add a status API that returns `load_router_config_from_env(os.environ).to_status()`. Add a status-page panel showing mode, selected provider order, configured providers, fallback status, and timeout.

- [x] **Step 4: Run static tests**

Run: `python -m unittest tests.test_static_app -v`
Expected: static tests pass.

### Task 4: Project State And Verification

**Files:**
- Modify: `docs/master_task_board.md`
- Modify: `docs/progress_board.md`
- Modify: `docs/artifact_registry.md`
- Modify: `docs/project_state.json`
- Create: `docs/multi_model_router_smoke_test.md`

- [x] **Step 1: Update project state**

Mark phase 16 implementation steps as ready for owner smoke test and add artifacts for `app/llm_router.py`, router tests, admin status UI, and smoke test.

- [x] **Step 2: Run full verification**

Run:

```text
python -m unittest discover -s tests -v
git diff --check
```

Expected: all tests pass and diff check reports no whitespace errors.

- [x] **Step 3: Restart local service and smoke test**

Restart `http://127.0.0.1:8765`, then verify:

- no API keys -> `/api/llm-router/status` reports local fallback
- fake-test behavior remains covered by automated tests
- existing chat still responds locally

- [x] **Step 4: Commit**

Commit with message:

```text
Implement multi-model router skeleton
```
