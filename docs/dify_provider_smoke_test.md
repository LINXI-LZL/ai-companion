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
