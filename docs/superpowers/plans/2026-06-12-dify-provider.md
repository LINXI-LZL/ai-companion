# Dify Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Dify Chat App as an optional external-brain provider in the existing companion router while preserving local safety, memory, media intent, and fallback behavior.

**Architecture:** Keep `app/orchestrator.py` as the local planner. Extend `app/llm_router.py` so `dify` is another provider next to OpenAI, DeepSeek, and Gemini, with Dify-specific request payload construction and response parsing. Pass the local user id from `app/server.py`, update the Run Status UI to show Dify readiness, and keep all secrets server-side.

**Tech Stack:** Python standard library (`json`, `urllib.request`, `unittest`, `unittest.mock`), existing SQLite-backed local app, existing static HTML/CSS/JS admin console.

---

## File Structure

- Modify `app/llm_router.py`: add Dify provider configuration, request-body building, `_call_dify`, timeout handling, long-output fallback, and redacted status.
- Modify `app/server.py`: pass `user_id` into the router so Dify gets a stable per-user `user` value.
- Modify `app/static/app.js`: add Chinese display labels for Dify and new fallback reasons.
- Modify `README.md`: document Dify provider mode and environment variables.
- Modify `tests/test_llm_router.py`: cover Dify config, request shape, response parsing, fallback, safety bypass, and output length.
- Modify `tests/test_storage_api.py`: cover server passing the user id to the router.
- Modify `tests/test_static_app.py`: cover UI and README-visible Dify support.
- Create `docs/dify_provider_smoke_test.md`: owner-facing smoke test checklist after implementation.
- Update `docs/artifact_registry.md`, `docs/master_task_board.md`, `docs/progress_board.md`, and `docs/project_state.json`: mark the Dify implementation plan and the implementation outputs created in this build round.

---

### Task 1: Dify Config And Redacted Status

**Files:**
- Modify: `app/llm_router.py`
- Test: `tests/test_llm_router.py`

- [ ] **Step 1: Write failing Dify config tests**

Add these tests to `tests/test_llm_router.py`:

```python
    def test_dify_config_status_redacts_secret_and_exposes_response_mode(self):
        from app.llm_router import load_router_config_from_env

        status = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "dify-secret-key",
                "DIFY_API_BASE_URL": "https://example.dify.local/v1",
                "DIFY_RESPONSE_MODE": "blocking",
                "DIFY_APP_USER_PREFIX": "treehole",
            }
        ).to_status()

        self.assertTrue(status["enabled"])
        self.assertEqual(status["active_provider"], "dify")
        self.assertTrue(status["providers"]["dify"]["configured"])
        self.assertEqual(status["providers"]["dify"]["model"], "Dify Chat App")
        self.assertEqual(status["providers"]["dify"]["response_mode"], "blocking")
        self.assertNotIn("dify-secret-key", str(status))

    def test_auto_mode_can_choose_dify_when_only_dify_is_configured(self):
        from app.llm_router import load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "auto",
                "DIFY_API_KEY": "dify-secret-key",
            }
        )

        self.assertEqual(config.choose_provider().name, "dify")
        self.assertIn("dify", config.to_status()["provider_order"])
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
python -m unittest tests.test_llm_router -v
```

Expected: failure because `dify` is not in `SUPPORTED_PROVIDERS` and `status["providers"]["dify"]` does not exist.

- [ ] **Step 3: Extend provider config**

In `app/llm_router.py`, change the provider constants and config dataclass to:

```python
SUPPORTED_PROVIDERS = ("openai", "deepseek", "gemini", "dify")
DEFAULT_DIFY_RESPONSE_MODE = "blocking"
DEFAULT_DIFY_USER_PREFIX = "wechat-treehole"


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    response_mode: str = ""
    user_prefix: str = ""

    @property
    def configured(self):
        return bool(self.api_key.strip())

    def to_status(self):
        status = {
            "configured": self.configured,
            "model": self.model,
        }
        if self.name == "dify":
            status["response_mode"] = self.response_mode or DEFAULT_DIFY_RESPONSE_MODE
        return status
```

Add Dify to `load_router_config_from_env`:

```python
        "dify": ProviderConfig(
            name="dify",
            api_key=_clean(env.get("DIFY_API_KEY")),
            model="Dify Chat App",
            base_url=_clean(env.get("DIFY_API_BASE_URL")) or "https://api.dify.ai/v1",
            response_mode=_normalized_dify_response_mode(env.get("DIFY_RESPONSE_MODE")),
            user_prefix=_clean(env.get("DIFY_APP_USER_PREFIX")) or DEFAULT_DIFY_USER_PREFIX,
        ),
```

Add this helper near `_normalized_mode`:

```python
def _normalized_dify_response_mode(value):
    mode = _clean(value).lower() or DEFAULT_DIFY_RESPONSE_MODE
    if mode == "blocking":
        return mode
    return DEFAULT_DIFY_RESPONSE_MODE
```

- [ ] **Step 4: Run config tests and verify pass**

Run:

```powershell
python -m unittest tests.test_llm_router.LlmRouterTests.test_dify_config_status_redacts_secret_and_exposes_response_mode tests.test_llm_router.LlmRouterTests.test_auto_mode_can_choose_dify_when_only_dify_is_configured -v
```

Expected: both tests pass.

- [ ] **Step 5: Commit Task 1**

```powershell
git add app/llm_router.py tests/test_llm_router.py
git commit -m "Add Dify router configuration"
```

---

### Task 2: Dify Request Body And Response Parsing

**Files:**
- Modify: `app/llm_router.py`
- Test: `tests/test_llm_router.py`

- [ ] **Step 1: Write failing request and adapter tests**

Add these tests to `tests/test_llm_router.py`:

```python
    def test_dify_request_uses_chat_messages_payload_shape(self):
        from app.llm_router import build_provider_request, load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
                "DIFY_APP_USER_PREFIX": "treehole",
            }
        )
        provider = config.providers["dify"]

        request = build_provider_request(
            provider,
            {
                "reply_text": "本地兜底",
                "safety_mode": False,
                "scenario": "work_boss",
                "mode": "text_plus_sticker",
                "sticker_intent": "sticker_speechless",
                "voice_intent": "none",
            },
            "老板又临下班改需求，真的离谱",
            ["用户喜欢短回复"],
            [{"incoming_text": "你好", "reply_text": "在呢"}],
            user_id="owner",
        )

        self.assertEqual(request["provider"], "dify")
        self.assertEqual(request["message"], "老板又临下班改需求，真的离谱")
        self.assertEqual(request["dify_payload"]["query"], "老板又临下班改需求，真的离谱")
        self.assertEqual(request["dify_payload"]["response_mode"], "blocking")
        self.assertEqual(request["dify_payload"]["user"], "treehole-owner")
        self.assertEqual(request["dify_payload"]["inputs"]["persona_style"], "刀子嘴豆腐心")
        self.assertEqual(request["dify_payload"]["inputs"]["scenario"], "work_boss")
        self.assertEqual(request["dify_payload"]["inputs"]["mode"], "text_plus_sticker")
        self.assertEqual(request["dify_payload"]["inputs"]["media_intent"], "sticker_speechless")
        self.assertEqual(request["dify_payload"]["inputs"]["voice_intent"], "none")
        self.assertEqual(request["dify_payload"]["inputs"]["local_reply"], "本地兜底")
        self.assertIn("用户喜欢短回复", request["dify_payload"]["inputs"]["memories"])
        self.assertIn("用户：你好", request["dify_payload"]["inputs"]["recent_history"])

    def test_dify_call_posts_chat_messages_and_reads_answer(self):
        from unittest.mock import patch

        from app.llm_router import _call_provider, build_provider_request, load_router_config_from_env

        config = load_router_config_from_env(
            {
                "COMPANION_LLM_PROVIDER": "dify",
                "DIFY_API_KEY": "secret",
                "DIFY_API_BASE_URL": "https://dify.example/v1",
            }
        )
        provider = config.providers["dify"]
        request = build_provider_request(
            provider,
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你是谁",
            [],
            [],
            user_id="owner",
        )

        with patch(
            "app.llm_router._post_json",
            return_value={"answer": "我是你的微信树洞 AI。", "conversation_id": "conv-1"},
        ) as post_json:
            raw = _call_provider(provider, request, 8)

        self.assertEqual(raw["text"], "我是你的微信树洞 AI。")
        self.assertEqual(raw["conversation_id"], "conv-1")
        url, headers, payload, timeout_seconds = post_json.call_args.args
        self.assertEqual(url, "https://dify.example/v1/chat-messages")
        self.assertEqual(headers["Authorization"], "Bearer secret")
        self.assertEqual(payload["response_mode"], "blocking")
        self.assertEqual(payload["query"], "你是谁")
        self.assertEqual(timeout_seconds, 8)
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
python -m unittest tests.test_llm_router.LlmRouterTests.test_dify_request_uses_chat_messages_payload_shape tests.test_llm_router.LlmRouterTests.test_dify_call_posts_chat_messages_and_reads_answer -v
```

Expected: failure because `build_provider_request` does not accept `user_id`, has no `dify_payload`, and `_call_provider` does not handle Dify.

- [ ] **Step 3: Add Dify request construction**

Change the signatures in `app/llm_router.py`:

```python
def route_external_reply(config, local_plan, message, memories=None, recent_messages=None, transport=None, user_id=""):
```

```python
def build_provider_request(provider, local_plan, message, memories, recent_messages, user_id=""):
```

Inside `route_external_reply`, call:

```python
    request = build_provider_request(provider, local_plan, message, memories or [], recent_messages or [], user_id=user_id)
```

Inside `build_provider_request`, return the existing prompt fields plus Dify payload:

```python
    return {
        "provider": provider.name,
        "model": provider.model,
        "message": message,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "dify_payload": _build_dify_payload(provider, local_plan, message, memories, recent_messages, user_id),
    }
```

Add these helpers:

```python
def _build_dify_payload(provider, local_plan, message, memories, recent_messages, user_id):
    return {
        "inputs": {
            "persona_style": PERSONA_STYLE,
            "scenario": local_plan.get("scenario") or "generic",
            "mode": local_plan.get("mode") or "text_only",
            "media_intent": local_plan.get("sticker_intent") or "none",
            "voice_intent": local_plan.get("voice_intent") or "none",
            "memories": "；".join(memories[:6]) if memories else "无",
            "recent_history": _format_recent_history(recent_messages),
            "local_reply": local_plan.get("reply_text", ""),
        },
        "query": message,
        "response_mode": provider.response_mode or DEFAULT_DIFY_RESPONSE_MODE,
        "user": _build_dify_user(provider, user_id),
    }


def _format_recent_history(recent_messages):
    history = []
    for item in list(recent_messages)[:6]:
        incoming = item.get("incoming_text", "")
        reply = item.get("reply_text", "")
        if incoming or reply:
            history.append(f"用户：{incoming}\nAI：{reply}")
    return "\n---\n".join(history) if history else "无"


def _build_dify_user(provider, user_id):
    safe_user = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in _clean(user_id))
    return f"{provider.user_prefix or DEFAULT_DIFY_USER_PREFIX}-{safe_user or 'anonymous'}"
```

- [ ] **Step 4: Add Dify adapter**

In `_call_provider`, add:

```python
    if provider.name == "dify":
        return _call_dify(provider, request, timeout_seconds)
```

Add `_call_dify`:

```python
def _call_dify(provider, request, timeout_seconds):
    data = _post_json(
        f"{provider.base_url.rstrip('/')}/chat-messages",
        {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        },
        request["dify_payload"],
        timeout_seconds,
    )
    return {
        "text": data.get("answer", ""),
        "conversation_id": data.get("conversation_id", ""),
    }
```

Extend `_coerce_text` so dict values can use `text` and `answer`:

```python
    if isinstance(value, dict):
        for key in ("reply_text", "text", "answer", "content", "output_text"):
            if value.get(key):
                return str(value[key])
```

Add provider metadata extraction:

```python
def _provider_metadata(value):
    if not isinstance(value, dict):
        return {}
    return {
        "conversation_id": str(value.get("conversation_id") or ""),
    }
```

- [ ] **Step 5: Run adapter tests and verify pass**

Run:

```powershell
python -m unittest tests.test_llm_router.LlmRouterTests.test_dify_request_uses_chat_messages_payload_shape tests.test_llm_router.LlmRouterTests.test_dify_call_posts_chat_messages_and_reads_answer -v
```

Expected: both tests pass.

- [ ] **Step 6: Commit Task 2**

```powershell
git add app/llm_router.py tests/test_llm_router.py
git commit -m "Add Dify chat message adapter"
```

---

### Task 3: Fallback Behavior And Server User Id

**Files:**
- Modify: `app/llm_router.py`
- Modify: `app/server.py`
- Test: `tests/test_llm_router.py`
- Test: `tests/test_storage_api.py`

- [ ] **Step 1: Write failing fallback and server tests**

In `tests/test_llm_router.py`, change the existing timeout test to raise `RuntimeError("boom")` when expecting `provider_error`, then add:

```python
    def test_provider_timeout_has_specific_fallback_reason(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: (_ for _ in ()).throw(TimeoutError("slow")),
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["provider"], "local")
        self.assertEqual(result["metadata"]["fallback_reason"], "provider_timeout")

    def test_provider_output_too_long_falls_back_to_local_reply(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env(
                {
                    "COMPANION_LLM_PROVIDER": "dify",
                    "DIFY_API_KEY": "secret",
                    "COMPANION_LLM_MAX_OUTPUT_CHARS": "12",
                }
            ),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: "这是一段明显超过长度限制的外部回复",
        )

        self.assertEqual(result["reply_text"], "本地兜底")
        self.assertEqual(result["metadata"]["fallback_reason"], "output_too_long")

    def test_dify_conversation_id_is_copied_to_metadata_without_changing_text(self):
        from app.llm_router import load_router_config_from_env, route_external_reply

        result = route_external_reply(
            load_router_config_from_env({"COMPANION_LLM_PROVIDER": "dify", "DIFY_API_KEY": "secret"}),
            {"reply_text": "本地兜底", "safety_mode": False, "scenario": "generic", "mode": "text_only"},
            "你好",
            memories=[],
            recent_messages=[],
            transport=lambda request: {"text": "Dify 回复", "conversation_id": "conv-1"},
        )

        self.assertEqual(result["reply_text"], "Dify 回复")
        self.assertEqual(result["metadata"]["conversation_id"], "conv-1")
```

In `tests/test_storage_api.py`, add:

```python
    def test_chat_passes_user_id_to_dify_router_request(self):
        from app.llm_router import load_router_config_from_env
        from app.server import create_chat_response
        from app.storage import Storage

        seen_requests = []

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            user = store.create_user("owner", "Owner", allowed=True)
            response = create_chat_response(
                store,
                {"user_id": user["id"], "message": "老板又改需求"},
                router_config=load_router_config_from_env(
                    {
                        "COMPANION_LLM_PROVIDER": "dify",
                        "DIFY_API_KEY": "secret",
                        "DIFY_APP_USER_PREFIX": "treehole",
                    }
                ),
                router_transport=lambda request: seen_requests.append(request) or "Dify 回复",
            )

        self.assertEqual(response["plan"]["llm"]["provider"], "dify")
        self.assertEqual(seen_requests[0]["dify_payload"]["user"], f"treehole-{user['id']}")
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
python -m unittest tests.test_llm_router tests.test_storage_api -v
```

Expected: failure because timeout uses generic `provider_error`, long output is truncated instead of falling back, conversation id is not copied, and `app/server.py` does not pass `user_id`.

- [ ] **Step 3: Implement specific fallback handling**

In `route_external_reply`, replace the current try/except block and candidate checks with:

```python
    try:
        raw_reply = transport(request) if transport else _call_provider(provider, request, config.timeout_seconds)
        candidate = _coerce_text(raw_reply).strip()
        provider_metadata = _provider_metadata(raw_reply)
    except TimeoutError:
        return _local_result(config, local_reply, "provider_timeout")
    except Exception:
        return _local_result(config, local_reply, "provider_error")

    if not candidate:
        return _local_result(config, local_reply, "empty_reply")
    if _looks_like_debug_output(candidate):
        return _local_result(config, local_reply, "debug_output")
    if classify_safety(candidate)["safety_mode"]:
        return _local_result(config, local_reply, "unsafe_reply")
    if len(candidate) > config.max_output_chars:
        return _local_result(config, local_reply, "output_too_long")

    metadata = {
        "enabled": True,
        "provider": provider.name,
        "model": provider.model,
        "fallback_reason": "",
        "mode": config.mode,
    }
    if provider_metadata.get("conversation_id"):
        metadata["conversation_id"] = provider_metadata["conversation_id"]
    return {
        "reply_text": candidate,
        "metadata": metadata,
    }
```

Remove the old `_fit_text(candidate, config.max_output_chars)` line from the success path. Keep `_fit_text` in the file only if another caller still uses it; otherwise delete `_fit_text`.

- [ ] **Step 4: Pass user id from server to router**

In `app/server.py`, update the router call:

```python
    routed = route_external_reply(
        router_config,
        plan,
        message,
        memories=memories,
        recent_messages=recent_messages,
        transport=router_transport,
        user_id=user_id,
    )
```

- [ ] **Step 5: Run routing and server tests and verify pass**

Run:

```powershell
python -m unittest tests.test_llm_router tests.test_storage_api -v
```

Expected: all router and storage/API tests pass.

- [ ] **Step 6: Commit Task 3**

```powershell
git add app/llm_router.py app/server.py tests/test_llm_router.py tests/test_storage_api.py
git commit -m "Harden Dify router fallback behavior"
```

---

### Task 4: Admin Status Labels And README

**Files:**
- Modify: `app/static/app.js`
- Modify: `README.md`
- Test: `tests/test_static_app.py`

- [ ] **Step 1: Write failing static docs test**

Add this test to `tests/test_static_app.py`:

```python
    def test_static_app_and_readme_expose_dify_provider_without_secrets(self):
        script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn('dify: "Dify"', script)
        self.assertIn("provider_timeout", script)
        self.assertIn("output_too_long", script)
        self.assertIn("DIFY_API_KEY", readme)
        self.assertIn("local | auto | openai | deepseek | gemini | dify", readme)
        self.assertNotIn("dify-secret-key", readme)
```

- [ ] **Step 2: Run the test and verify failure**

Run:

```powershell
python -m unittest tests.test_static_app.StaticAppTests.test_static_app_and_readme_expose_dify_provider_without_secrets -v
```

Expected: failure because the UI and README do not mention Dify yet.

- [ ] **Step 3: Update UI labels**

In `app/static/app.js`, add Dify to `displayLabel`:

```javascript
    dify: "Dify",
```

In `llmFallbackLabel`, add:

```javascript
    provider_timeout: "外部模型请求超时，已回到本地",
    output_too_long: "外部模型回复过长，已回到本地",
```

- [ ] **Step 4: Update README provider docs**

In `README.md`, replace the supported mode list with:

```text
local | auto | openai | deepseek | gemini | dify
```

Add this Dify example under "Optional External Brain":

```powershell
$env:COMPANION_LLM_PROVIDER='dify'
$env:DIFY_API_KEY='your-dify-key'
$env:DIFY_API_BASE_URL='https://api.dify.ai/v1'
$env:DIFY_RESPONSE_MODE='blocking'
$env:DIFY_APP_USER_PREFIX='wechat-treehole'
```

Add this sentence:

```markdown
Dify is used through its Chat App `/chat-messages` API. The app sends structured local context to Dify, but local safety and local fallback stay in control.
```

- [ ] **Step 5: Run static docs test and verify pass**

Run:

```powershell
python -m unittest tests.test_static_app.StaticAppTests.test_static_app_and_readme_expose_dify_provider_without_secrets -v
```

Expected: the test passes.

- [ ] **Step 6: Commit Task 4**

```powershell
git add app/static/app.js README.md tests/test_static_app.py
git commit -m "Document Dify provider status"
```

---

### Task 5: Smoke Test, Project State, And Full Verification

**Files:**
- Create: `docs/dify_provider_smoke_test.md`
- Modify: `docs/artifact_registry.md`
- Modify: `docs/master_task_board.md`
- Modify: `docs/progress_board.md`
- Modify: `docs/project_state.json`

- [ ] **Step 1: Create owner smoke test doc**

Create `docs/dify_provider_smoke_test.md`:

```markdown
# Dify Provider Smoke Test

## Goal

Verify that Dify can be used as the optional external brain without breaking local fallback, safety, or the Run Status page.

## Test 1: No Dify Key

Precondition: start the app without `DIFY_API_KEY`.

Steps:

1. Open `http://127.0.0.1:8765`.
2. Go to `运行状态`.
3. Check `外部主脑`.
4. Send `你是谁` in `聊天模拟`.

Expected result:

- The app keeps running.
- The status shows local fallback or provider-not-configured.
- Chat returns a Chinese reply.

## Test 2: Dify Mode Without Key

Precondition: start the app with `COMPANION_LLM_PROVIDER=dify` and no `DIFY_API_KEY`.

Steps:

1. Open `运行状态`.
2. Send `老板又改需求` in `聊天模拟`.

Expected result:

- The app does not crash.
- Fallback reason says the provider is not configured.
- Chat still returns a local reply.

## Test 3: Dify Mode With Key

Precondition: start the app with `COMPANION_LLM_PROVIDER=dify`, `DIFY_API_KEY`, and `DIFY_API_BASE_URL`.

Steps:

1. Send `你是谁`.
2. Send `嗳`.
3. Send `什么意思`.
4. Send `老板又临下班改需求，真的离谱`.

Expected result:

- Replies are Chinese and coherent.
- Replies do not include JSON, English debug labels, or provider names.
- Run Status shows Dify as configured.

## Test 4: Safety Still Local

Precondition: Dify mode is configured.

Steps:

1. Send a high-risk self-harm style message.

Expected result:

- The reply uses the serious local safety response.
- The fallback reason is `safety_mode`.
- No playful sticker or voice mode is used.
```

- [ ] **Step 2: Update project tracking docs**

Update:

- `docs/artifact_registry.md`: add artifacts for `Dify provider implementation plan`, `Dify provider source`, `Dify provider tests`, and `Dify provider smoke test`.
- `docs/master_task_board.md`: mark Dify design review and implementation plan done; add implementation, docs, verification, and owner smoke test rows.
- `docs/progress_board.md`: move current position to Dify owner smoke test after implementation.
- `docs/project_state.json`: set phase 18 implementation steps and artifacts with stable ids.

Use these ids:

```text
artifact-065 Dify provider implementation plan
artifact-066 Dify provider source
artifact-067 Dify provider tests
artifact-068 Dify provider smoke test
step-18-03-dify-implementation-plan
step-18-04-dify-router-config
step-18-05-dify-adapter
step-18-06-dify-fallback-server-ui
step-18-07-dify-owner-smoke-test
```

- [ ] **Step 3: Run full automated verification**

Run:

```powershell
python -m unittest discover -s tests -v
git diff --check
```

Expected:

- all tests pass
- `git diff --check` reports no whitespace errors

- [ ] **Step 4: Commit Task 5**

```powershell
git add docs/dify_provider_smoke_test.md docs/artifact_registry.md docs/master_task_board.md docs/progress_board.md docs/project_state.json
git commit -m "Prepare Dify provider smoke test"
```

---

## Final Verification

Run:

```powershell
python -m unittest discover -s tests -v
git diff --check
git status --short
```

Expected:

- all unit tests pass
- diff check has no whitespace errors
- status is clean after the final commit

## Execution Handoff

Recommended execution mode: Subagent-Driven, because each task is small and has its own tests and commit boundary.

Alternative execution mode: Inline Execution, if the owner wants one continuous implementation session with fewer handoff messages.
