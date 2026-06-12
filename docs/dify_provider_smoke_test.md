# Dify Provider Smoke Test

Use this checklist after the Dify provider build is installed. The goal is to confirm that Dify can act as the optional external brain while local fallback and local safety still stay in control.

## Prerequisites

- A Dify Chat App with API access enabled.
- `DIFY_API_KEY` for the Dify Chat App.
- Optional: `DIFY_API_BASE_URL` when using a self-hosted or non-default Dify endpoint. Default is `https://api.dify.ai/v1`.
- Optional: `DIFY_RESPONSE_MODE`. Current supported mode is `blocking`; unsupported values are normalized back to `blocking`.
- Local app can be started with:

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m app.server --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

## Test 1: Local Mode Without Any Dify Key

**Goal:** Prove the app still works locally when no Dify credential exists.

**Setup:**

```powershell
Remove-Item Env:DIFY_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:DIFY_API_BASE_URL -ErrorAction SilentlyContinue
$env:COMPANION_LLM_PROVIDER='local'
```

**Steps:**

1. Start the local app.
2. Open the Chat Simulator.
3. Send a normal message such as `老板又临下班改需求，真的离谱`.
4. Open Run Status.

**Expected result:**

- The chat returns a local companion reply.
- Run Status shows local fallback/local mode.
- The JSON plan, if inspected, shows `provider` as `local` and `fallback_used=true`.

## Test 2: Dify Mode Without `DIFY_API_KEY`

**Goal:** Prove explicit Dify mode does not break the app when the key is missing.

**Setup:**

```powershell
Remove-Item Env:DIFY_API_KEY -ErrorAction SilentlyContinue
$env:COMPANION_LLM_PROVIDER='dify'
```

**Steps:**

1. Restart the local app.
2. Send a normal message in the Chat Simulator.
3. Open Run Status or inspect the `/api/chat` JSON response.

**Expected result:**

- The chat still returns a local companion reply.
- The response falls back locally.
- The fallback reason should identify provider unavailability. In this build, missing credentials may be shown as `provider_not_configured`; if surfaced with owner-facing wording, treat this as the `provider_unavailable` no-key path.

## Test 3: Dify Mode With A Real Key

**Goal:** Prove the Dify Chat App can answer through the provider route.

**Setup:**

```powershell
$env:COMPANION_LLM_PROVIDER='dify'
$env:DIFY_API_KEY='your-real-dify-key'
$env:DIFY_API_BASE_URL='https://api.dify.ai/v1'
$env:DIFY_RESPONSE_MODE='blocking'
```

**Steps:**

1. Restart the local app.
2. Send a short normal message, for example `你是谁` or `老板又改需求`.
3. Open Run Status or inspect the `/api/chat` JSON response.

**Expected result:**

- The reply comes back successfully.
- The JSON plan shows provider `dify`.
- `fallback_used=false`.
- `conversation_id` may appear in metadata when Dify returns one.
- Run Status shows Dify as configured without exposing the API key.

## Test 4: Local Safety Remains In Control

**Goal:** Prove crisis/self-harm content is handled by local safety instead of being blindly sent to Dify.

**Setup:** Use either local mode or configured Dify mode.

**Steps:**

1. Send a self-harm or crisis-style message in the Chat Simulator.
2. Inspect the reply and the response metadata.

**Expected result:**

- The app returns the local safety reply/fallback.
- Dify is not relied on for this response.
- The JSON plan should show safety handling and local fallback, not an unrestricted Dify answer.

## Deferred Items

Real WeChat/WeCom encrypted callback verification and real media assets remain deferred. This smoke test only covers the local simulator, Dify provider routing, fallback behavior, and local safety boundary.
