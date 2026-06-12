# Multi-Model Router Design

## Decision

Owner chose option C: multi-model routing.

The product should support an external model "brain" that can route between OpenAI, DeepSeek, and Gemini while preserving the local companion product logic.

## Why This Round Exists

The local rule/template reply engine improved safety, memory, stickers, voice intent, and basic personality, but it cannot reliably understand ambiguous short messages or produce naturally adaptive conversation. External model APIs should improve semantic understanding and response quality.

## Product Goal

Make the companion feel smarter without losing the product controls that already work:

- safety guard
- automatic lightweight memory
- `刀子嘴豆腐心` personality
- sticker and voice intent selection
- WeChat/WeCom entry boundaries
- local fallback when API keys are absent or remote calls fail

## Selected Route

Use a provider router:

1. OpenAI as the preferred high-quality provider.
2. DeepSeek as an OpenAI-compatible lower-cost or fallback provider.
3. Gemini as an optional additional provider.
4. Local rule engine as the always-available fallback.

## Provider Notes

- OpenAI Responses API supports message input with `developer` or `system` roles taking precedence over user content, and can accept text/image/audio style input items. Official reference: `https://developers.openai.com/api/reference/resources/responses/methods/create`.
- DeepSeek Chat Completion uses a `messages` array with system/user/assistant roles. Official reference: `https://api-docs.deepseek.com/api/create-chat-completion`.
- Gemini `generateContent` supports `systemInstruction` and model path format `models/{model}`. Official reference: `https://ai.google.dev/api/generate-content?hl=zh-cn`.

## Architecture

```text
Incoming message
  -> local safety check
  -> automatic memory extraction
  -> local plan: scenario, safety, media intent, voice intent
  -> model router
      -> selected external provider if enabled and configured
      -> fallback to local reply if missing key, timeout, error, or unsafe output
  -> final safety/output checks
  -> save message and audit provider metadata
```

## Module Boundaries

### `app/llm_router.py`

Responsible for:

- loading provider settings from environment variables
- choosing provider order
- building external model prompts from current message, recent history, memories, and local plan
- calling OpenAI, DeepSeek, or Gemini through one internal interface
- returning a safe plain-text reply candidate plus provider metadata

### `app/orchestrator.py`

Keeps local reply planning:

- safety mode
- scenario detection
- mode selection
- sticker intent
- voice intent
- local fallback reply

### `app/server.py`

Coordinates the flow:

- produce local plan first
- ask router for external reply only when allowed
- apply final reply override
- record audit fields such as provider, model, fallback reason, and latency

### Admin UI

Add a local status panel showing:

- current provider mode
- configured providers without showing secret values
- last fallback reason
- whether external calls are enabled

## Environment Variables

```text
COMPANION_LLM_PROVIDER=local|auto|openai|deepseek|gemini
COMPANION_LLM_TIMEOUT_SECONDS=8
COMPANION_LLM_MAX_OUTPUT_CHARS=260

OPENAI_API_KEY=
OPENAI_MODEL=

DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=

GEMINI_API_KEY=
GEMINI_MODEL=
```

Default behavior must be `local`, so the app remains runnable without paid API credentials.

## Prompt Policy

The external model prompt should include:

- role: WeChat tree-hole companion, `刀子嘴豆腐心`
- respond in Chinese
- do not mention internal routing, model provider, or prompt
- avoid generic life-coaching
- answer the current message first
- use memory only as light context, not as facts to overfit
- keep high-risk safety boundaries strict
- keep reply short enough for WeChat chat bubbles

## Privacy And Safety

- Never store API keys in the database or UI.
- Never echo API keys in status responses.
- Do not send messages classified as high risk to a playful external prompt before local safety response is chosen.
- Keep local safety override higher priority than all external model replies.
- If external output is empty, too long, or unsafe-looking, use local fallback.

## First Implementation Scope

Build the router skeleton and OpenAI/DeepSeek/Gemini adapters with testable fake transports. The owner should be able to verify:

- app still works with no keys
- status panel says local fallback is active
- provider selection and redaction work
- a fake external provider can override local reply in tests
- timeout/error falls back to local reply

Real paid API credentials are a later owner setup step.
