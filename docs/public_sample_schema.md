# Public Sample Schema

## Purpose

This schema converts public dialogue, sticker, and voice-emotion sources into one product-friendly format. It is designed for behavior distillation, not raw data dumping.

## JSONL Record Shape

Each record should be one JSON object per line:

```json
{
  "id": "sample-0001",
  "source_ids": ["source-cped"],
  "source_type": "public_dataset_or_synthetic_seed",
  "license_tier": "permissive_or_research_reference_or_synthetic",
  "scenario": "late_night_emo",
  "user_state": {
    "emotion": "tired",
    "intensity": 3,
    "risk_level": "low",
    "topic": "life_pressure"
  },
  "conversation_context": [
    {
      "speaker": "user",
      "content_type": "text",
      "content": "sanitized or synthetic user message"
    }
  ],
  "assistant_action": {
    "mode": "text_plus_sticker",
    "text_intent": "receive_emotion_then_light_joke",
    "sticker_intent": "supportive_mocking",
    "voice_intent": "none",
    "safety_mode": false
  },
  "target_behavior": {
    "reply_style": "short, warm, slightly sharp",
    "follow_up_count": 1,
    "avoid": ["sermon", "therapy_claim", "long_solution_dump"]
  },
  "notes": "Explain what behavior this sample teaches."
}
```

## Field Rules

| Field | Rule |
|---|---|
| `source_ids` | Must reference `data/public_sources/data_sources.json`; use `synthetic-seed` for generated examples |
| `source_type` | Distinguish public dataset, paper reference, method reference, and synthetic seed |
| `license_tier` | Keep license risk visible in every derived sample |
| `scenario` | Use product scenarios such as `late_night_emo`, `work_rant`, `relationship_rant`, `sleep_companion` |
| `risk_level` | Use `low`, `medium`, `high`; high risk must trigger safety mode |
| `mode` | Use `text_only`, `text_plus_sticker`, `sticker_only`, `short_voice`, `text_plus_short_voice`, or `safety_response` |
| `content` | Do not store raw copyrighted or private text unless license and privacy are confirmed |
| `notes` | Explain the behavior lesson, not just the text content |

## Multimodal Action Labels

| Label | Meaning |
|---|---|
| `sticker_reaction_mocking` | A light teasing reaction, useful when the user is annoyed but not distressed |
| `sticker_supportive_hug` | A comforting visual reaction for sadness or loneliness |
| `sticker_speechless` | A nonverbal reaction when the situation is absurd |
| `voice_sleepy_companion` | Short, slow voice message for late-night reassurance |
| `voice_serious_grounding` | Short serious voice-style response when the user is overwhelmed |
| `text_micro_followup` | One concise follow-up question to keep the conversation alive |
| `text_roast_then_reframe` | Light roast followed by a practical reframing |

## Safety Rule

When `risk_level` is `high`, the only allowed mode is `safety_response`. In that state, the agent must not use toxic teasing, jokes, sticker-only replies, or playful voice.

