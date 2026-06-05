# Auto Lightweight Memory Design

## Decision

Use option A: automatic lightweight memory. The companion should learn small stable preferences and repeated context from chat without requiring the user to manually add memory.

## Product Goal

Make the companion feel more like a real friend who remembers useful context while keeping privacy risk low.

## Scope

This change adds rule-based automatic memory extraction to the local companion flow. It does not add private chat scraping, vector storage, full summarization, or cloud model-based memory extraction.

## What The Agent May Remember

- Stable style preferences, such as `用户喜欢短回复`.
- Accepted companion style, such as `用户接受损友式吐槽`.
- Repeated work pressure themes, such as `用户最近反复被工作/老板改需求困扰`.
- Repeated late-night or sleep companion needs, such as `用户常在睡前需要陪伴`.

## What The Agent Must Not Remember

- Identity numbers, phone numbers, addresses, bank cards, passwords, tokens, secrets, API keys, or credential-like strings.
- High-risk self-harm wording or crisis content.
- One-off private details that are not stable preferences or repeated patterns.

## User Experience

The Memory page should read as an automatic memory manager, not a manual data-entry task. The owner can inspect, clear, and later delete memories, but normal users should not need to manually type memory items.

## Acceptance Criteria

- Sending a clear preference like `以后跟我说短点` automatically saves `用户喜欢短回复`.
- Sending repeated work-rant messages automatically saves a work-pressure memory once, without duplicate spam.
- Sending sensitive content such as tokens or phone numbers does not save memory.
- Sending high-risk self-harm content does not save memory.
- Existing explicit memory commands like `记住：用户喜欢短回复` still work.
- The Memory page labels automatic memory clearly.
