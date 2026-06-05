# Public Sample Distillation Plan

## Goal

Create a public-source behavior foundation for 微信树洞 AI so the agent feels more like a real late-night friend without requiring the user to manually provide private WeChat samples.

This phase focuses on:

- Chinese casual chat rhythm.
- Emotional-support flow.
- Sharp-tongued but protective friend tone.
- Sticker and emoji timing.
- Voice-message decision rules.
- Safety mode transitions.

It does not download large sticker packs, audio files, video files, or multi-GB archives while the user is using VPN traffic.

## Source Tiers

| Tier | Sources | Product Use |
|---|---|---|
| Primary candidates | CPED, CDial-GPT/LCCC, StickerConv, LiveChat | Distill reusable behavior rules after license and quality checks |
| Research references | ESConv, SoulChat, EmotionTalk, StickerInt, STICKERCONV paper | Learn support strategies, speech emotion design, and sticker-selection methods |
| Method references | LLM Roleplay, Character-LLM, OpenPersona, awesome-persona-distill-skills | Learn persona distillation structure and synthetic data generation methods |
| Deferred assets | U-Sticker sticker archives, EmotionTalk audio/video, large LCCC downloads | Download only after VPN is off and after a source-specific license check |

## Distillation Strategy

The project should avoid copying public dialogue lines into the final agent. Instead, public sources should be transformed into a behavior guide:

1. Identify the user state: relaxed, annoyed, anxious, sad, tired, lonely, angry, joking, or high-risk.
2. Choose a response mode: text only, text plus sticker, sticker only, short voice, or serious safety response.
3. Choose the conversational move: receive emotion, joke lightly, ask one short follow-up, mirror phrasing, reframe, summarize, or invite rest.
4. Apply the deep-night sharp-friend style: short sentences, light sarcasm, warm bottom line, no sermon.
5. Check safety: if self-harm, violence, illegal action, or severe crisis is detected, disable joking and switch to serious support.

## Output Artifacts

| Artifact | Purpose |
|---|---|
| `data/public_sources/data_sources.json` | Source manifest with license, traffic level, and recommended use |
| `docs/public_sample_schema.md` | Unified sample schema for text, sticker, voice, and behavior labels |
| `samples/public/seed_behavior_examples.jsonl` | Synthetic seed examples generated from the confirmed product behavior, not copied from public data |
| `docs/behavior_distillation_rules.md` | First version of distilled behavior rules |

## Download Policy

For now:

- Do not download sticker files from U-Sticker.
- Do not download EmotionTalk audio/video.
- Do not download full LCCC large archives.
- Do not clone large repositories or model weights.
- Do not use private or leaked chat logs.

When VPN is off, the user can manually download deferred assets. The next architecture phase should add exact local paths and checksums after download.

## License Handling

Use sources with permissive licenses for product candidates. Treat non-commercial, research-only, or unclear licenses as research references unless a later review confirms product use is allowed.

For final product assets:

- Prefer self-created or properly licensed sticker packs.
- Prefer generated or consented voice assets.
- Avoid voice cloning of any real person without explicit consent.
- Keep public data as behavior inspiration, not copied product content.

