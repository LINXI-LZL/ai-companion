# Module Boundary

## Boundary Principles

Each module should have one clear product responsibility. The goal is not to make the system complicated; it is to keep future changes from breaking unrelated parts. For example, if WeChat changes one message field, only the WeChat Channel Adapter should need changes.

## Module List

| Module | Product Responsibility | Owns | Does Not Own |
|---|---|---|---|
| WeChat Channel Adapter | Connect the product to Enterprise WeChat / WeChat customer-service style messaging | Webhook verification, message fetch, message send, platform-specific IDs, media upload wrapper | AI reply logic, user memory rules, safety decisions |
| Message Inbox + Normalizer | Turn all inbound platform messages into one internal event format | Internal message schema, deduplication, retry status | WeChat API secrets, prompt design |
| Safety Guard | Decide whether playful mode is allowed | Risk labels, safety mode, joke/sticker/voice bans | Final long-form AI response, diagnosis |
| User + Whitelist Service | Manage inner-test users | User identity, whitelist, status, per-user settings | Raw conversation content storage by default |
| Memory Service | Remember limited user preferences | Nickname, tone preference, common pressure sources, memory clear controls | Sensitive personal dossiers, full chat archives |
| Conversation Orchestrator | Decide the next companion response | Context assembly, prompt package, response plan, model routing | WeChat API calls, final media file hosting |
| Personality Engine | Keep the "late-night sharp friend" voice stable | Voice rules, tone limits, examples, anti-AI rules | Safety override, media file choice |
| Multimodal Decision Layer | Choose text, sticker intent, short voice script, or safety response | Response mode, sticker intent, voice intent, text fallback | Media copyright, voice provider credentials |
| Media Asset Layer | Attach real media when approved | Sticker pack registry, voice provider adapter, media IDs | Whether the conversation should use media |
| Public Sample Distillation | Turn public sources into behavior rules | Source manifest, license tier, seed examples, behavior labels | Private WeChat chat scraping, raw asset downloading by default |
| Admin Console API | Give the owner control over the MVP | User list, settings, source status, health summary | Direct WeChat platform calls from the browser |
| Audit + Observability | Make failures visible | Error logs, message status, safety events, cost counters | User-facing conversation style |

## Internal Data Shapes

### Inbound Message

```json
{
  "id": "msg_001",
  "channel": "wecom_kf",
  "external_user_id": "external_user_x",
  "content_type": "text",
  "content": "今天真的累到不想说话，但又睡不着。",
  "received_at": "2026-06-05T14:52:45+08:00"
}
```

### Response Plan

```json
{
  "mode": "text_plus_short_voice",
  "safety_mode": false,
  "text_intent": "receive_emotion_then_companion",
  "sticker_intent": "sticker_supportive_hug",
  "voice_intent": "voice_sleepy_companion",
  "follow_up_count": 1
}
```

### Memory Record

```json
{
  "user_id": "user_owner",
  "key": "tone_preference",
  "value": "lightly sharp, not long-winded",
  "source": "explicit_admin_setting",
  "clearable": true
}
```

## Module Interaction Rules

- Safety Guard runs before Personality Engine can add jokes.
- Multimodal Decision Layer must respect Safety Guard.
- Media Asset Layer can fail without blocking text fallback.
- Public Sample Distillation can update behavior rules, but it cannot write user memory.
- Admin Console changes configuration; it does not directly send WeChat messages.
- WeChat Channel Adapter never stores raw chat content unless a retention rule allows it.

## Testing Boundaries

| Test Area | What To Verify |
|---|---|
| WeChat adapter | Platform event becomes normalized inbound message |
| Safety | High-risk message disables jokes, stickers, and playful voice |
| Memory | Memory can be used, disabled, and cleared per user |
| Multimodal | Correct mode is chosen for late-night, work-rant, self-mockery, and high-risk cases |
| Admin | Setting changes affect later response plans |
| Distillation | Research-only sources cannot be marked product-ready by accident |

