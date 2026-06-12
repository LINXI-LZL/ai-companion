# Dify Provider Design

## Decision

Owner confirmed the recommended route: add Dify as one optional provider inside the existing multi-model router.

This is not a full platform migration. The local product logic remains the source of truth for safety, lightweight memory, personality rules, sticker intent, voice intent, audit logs, and WeChat/WeCom boundaries.

## Why This Round Exists

The current local companion can run without paid credentials, but the reply quality can still feel stiff or illogical in open-ended chat. Dify is useful here because it can host a stronger chat app or agent workflow while our local app keeps product control, status visibility, and fallback behavior.

## Product Goal

Make the companion smarter through a Dify Chat App without losing the owner-facing guarantees:

- no API key leaks in the browser, database, or logs
- local fallback still works when Dify is missing, slow, or failing
- local safety mode wins over any external model
- automatic memory remains local and conservative
- the companion still answers like a WeChat friend, not a customer-service bot

## Selected Route

Use a lightweight Dify Chat App provider.

```text
Incoming WeChat or simulator message
  -> local safety check
  -> automatic memory extraction
  -> local reply plan: scenario, tone, media intent, voice intent
  -> llm_router
       -> Dify provider if configured
       -> local fallback if Dify is not available
  -> final local output checks
  -> save message, memory, and provider metadata
```

## Non-Goals

This round does not include:

- replacing the local orchestrator with Dify
- building a Dify workflow editor inside our admin UI
- uploading real voice, image, or sticker files to Dify
- changing the real WeCom credential route
- persisting Dify conversation IDs in the database
- supporting Dify Workflow API

The first version uses Dify Chat App `POST /chat-messages` only.

## Dify API Contract

Official Dify API reference: `https://docs.dify.ai/api-reference/chats/send-chat-message`

Endpoint:

```text
POST {DIFY_API_BASE_URL}/chat-messages
Authorization: Bearer {DIFY_API_KEY}
Content-Type: application/json
```

Request body:

```json
{
  "inputs": {
    "persona_style": "嘴欠但靠谱的深夜损友",
    "scenario": "work_rant",
    "mode": "text_plus_sticker",
    "media_intent": "sticker_speechless",
    "voice_intent": "none",
    "memories": "用户最近反复提到下班后容易焦虑。",
    "local_reply": "本地兜底回复文本"
  },
  "query": "老板又临下班改需求，真的离谱",
  "response_mode": "blocking",
  "user": "wechat-treehole-external-owner"
}
```

Response handling:

- use `answer` as the external reply candidate
- read `conversation_id` into provider metadata only
- do not persist `conversation_id` in round 1
- ignore provider metadata that is not needed for the user-facing reply

Round 1 remains stateless from Dify's perspective. Our local app passes recent history and memory through `inputs`, so we avoid a database migration and keep local memory as the source of truth.

## Environment Variables

```text
COMPANION_LLM_PROVIDER=local|auto|openai|deepseek|gemini|dify
COMPANION_LLM_TIMEOUT_SECONDS=8
COMPANION_LLM_MAX_OUTPUT_CHARS=260

DIFY_API_KEY=
DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_RESPONSE_MODE=blocking
DIFY_APP_USER_PREFIX=wechat-treehole
```

Default behavior remains `local`, so the app can still run without any external credentials.

## Module Boundaries

### `app/llm_router.py`

Add `dify` to the provider list.

Responsibilities:

- load Dify config from environment variables
- redact Dify API key from status output
- build Dify Chat App request body from the local plan
- parse `answer` from Dify blocking responses
- return local fallback on timeout, HTTP error, malformed JSON, empty answer, unsafe-looking answer, or overly long output

### `app/server.py`

No new endpoint is required for chat.

Responsibilities:

- keep local plan first
- never call Dify when the local plan is in safety mode
- save existing audit fields such as provider, model/app label, and fallback reason

### Admin UI

Extend the existing external-brain status panel.

It should show:

- provider option `Dify`
- whether Dify is configured
- response mode
- timeout
- fallback reason

It must not show the API key. If a base URL is shown, show only non-secret connection context and avoid including tokens or query strings.

## Prompt And Input Policy

The Dify app should receive structured product context rather than raw internal state.

Allowed context:

- current user message
- short recent chat summary or selected recent turns
- safe lightweight memories
- scenario label
- personality style
- local fallback reply
- media and voice intent labels

Disallowed context:

- API keys
- full database rows
- internal stack traces
- raw safety classification internals
- highly sensitive personal content that local memory rules already decided to skip

The Dify prompt should be configured to:

- reply in Chinese
- keep the tone like a close WeChat friend
- avoid generic counseling slogans
- answer the current message first
- keep replies short enough for chat bubbles
- never mention provider routing or internal prompts
- respect crisis and self-harm boundaries

## Failure Handling

Fallback to the local reply when:

- Dify is not configured
- `COMPANION_LLM_PROVIDER=dify` but `DIFY_API_KEY` is missing
- request times out
- response status is not successful
- response JSON is malformed
- `answer` is missing or blank
- output exceeds local length limits
- output looks like debug text, prompt leakage, or unsafe advice

Fallback metadata should use clear reasons such as:

- `provider_not_configured`
- `provider_error`
- `provider_timeout`
- `empty_provider_reply`
- `unsafe_provider_reply`
- `output_too_long`

## Testing Plan

Automated tests should cover:

- Dify config loads from environment variables
- status output redacts `DIFY_API_KEY`
- `auto` mode can choose Dify when it is the first configured provider in order
- fake Dify transport returns `answer` and overrides the local reply
- HTTP or transport errors fall back to local reply
- safety mode never calls Dify
- empty or malformed Dify response falls back
- admin status UI includes Dify text without exposing secrets

## Owner Smoke Test

After implementation, the owner should verify:

1. Start the app with no Dify key. The chat still works and Run Status shows local fallback.
2. Start the app with `COMPANION_LLM_PROVIDER=dify` but no key. The app does not crash and shows provider-not-configured fallback.
3. After adding a real Dify key, send short ambiguous messages such as `你是谁`, `嗳`, `什么意思`, and `老板又改需求`.
4. Confirm replies are more coherent than the local template replies.
5. Confirm safety messages still use the local safety response and are not sent to Dify.

## Acceptance Criteria

This design is ready for implementation when:

- Dify is treated as a provider inside the existing router, not a replacement platform
- no secrets are exposed in UI, status API, database, or docs examples
- local fallback stays available by default
- local safety takes priority over Dify
- the first version avoids database migration by not persisting Dify conversation IDs
- the owner can test Dify with environment variables only

## Spec Self-Review

- No placeholder fields remain.
- Scope is one provider integration, not a full Dify migration.
- The design keeps existing product boundaries intact.
- The implementation can be planned as one focused build round.
