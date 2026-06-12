# Dify Provider Smoke Test

Use this checklist after the Dify provider build is installed.

## Goal

Verify that Dify can be used as the optional external brain without breaking local fallback, safety, or the Run Status page.

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

## Test 1: No Dify Key

**Goal:** Prove the app still works locally when no Dify credential exists.

**Precondition:** Start the app without `DIFY_API_KEY`.

Optional cleanup:

```powershell
Remove-Item Env:DIFY_API_KEY -ErrorAction SilentlyContinue
```

Note: the default/local mode is enough for this test; do not add a Dify key.

**Steps:**

1. Start the local app.
2. Open `http://127.0.0.1:8765`.
3. Go to `运行状态`.
4. Check `外部主脑`.
5. Go to `聊天模拟`.
6. Send `你是谁`.

**Expected result:**

- The app keeps running.
- Status shows local fallback or `provider_not_configured`.
- Chat returns a Chinese reply.

## Test 2: Dify Mode Without `DIFY_API_KEY`

**Goal:** Prove explicit Dify mode does not break the app when the key is missing.

**Setup:**

```powershell
Remove-Item Env:DIFY_API_KEY -ErrorAction SilentlyContinue
$env:COMPANION_LLM_PROVIDER='dify'
```

**Steps:**

1. Restart the local app.
2. Go to `聊天模拟`.
3. Send `老板又改需求`.
4. Open `运行状态`.
5. Check the external-brain fallback status or inspect the `/api/chat` JSON response.

**Expected result:**

- The app does not crash.
- The fallback reason says the provider is not configured: `provider_not_configured`.
- Chat still returns a local reply.

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
2. Go to `聊天模拟`.
3. Send `你是谁`.
4. Send `嗳`.
5. Send `什么意思`.
6. Send `老板又临下班改需求，真的离谱`.
7. Open Run Status or inspect the `/api/chat` JSON response.

**Expected result:**

- Replies are Chinese and coherent.
- Replies do not include JSON, English debug labels, or provider names.
- Run Status shows Dify as configured.
- The JSON plan shows provider `dify`.
- `fallback_used=false`.
- `conversation_id` may appear in metadata when Dify returns one.

## Test 4: Local Safety Remains In Control

**Goal:** Prove crisis/self-harm content is handled by local safety instead of being blindly sent to Dify.

**Precondition:** Dify mode is configured with a real key.

**Steps:**

1. Send a self-harm or crisis-style message in the Chat Simulator.
2. Inspect the reply and the response metadata.

**Expected result:**

- The app returns a serious local safety response.
- The fallback reason is exactly `safety_mode`.
- No playful sticker or voice mode is used.
- Dify is not relied on for this response.

## Deferred Items

Real WeChat/WeCom encrypted callback verification and real media assets remain deferred. This smoke test only covers the local simulator, Dify provider routing, fallback behavior, and local safety boundary.
