# 微信树洞 AI Design Spec

## Summary

微信树洞 AI is a WeChat-entry AI companion for the owner and a small group of invited friends. The MVP centers on late-night stress, emo moments, and sleep-time companionship. The agent's personality is a mixed "sharp-tongued late-night friend": playful, lightly toxic, protective, emotionally present, and able to become serious when safety requires it.

## Confirmed Decisions

- Personality: B + D, a sharp-tongued friend combined with late-night companionship.
- MVP scenario: life pressure, emo, and sleep-time companionship.
- Initial audience: the owner and a few invited friends.
- WeChat route: Enterprise WeChat or WeChat customer-service style entry.
- Product strategy: hybrid. Confirm blueprint, confirm static prototype, then plan architecture and implementation rounds.

## Product Experience

The user should feel they are messaging a familiar friend, not using a formal support bot. The AI should respond in short, conversational messages. It should first acknowledge the mood, then match the user's tone, and only then help untangle the situation if that feels welcome.

Example voice:

> 行，今天又是谁把你气成这样了？你先骂，我负责帮你把逻辑捋顺，顺便判断一下是不是你也有点上头。

The AI must avoid fake medical authority. It can provide emotional support and practical grounding, but it must not claim to diagnose, treat, or replace professional help.

## MVP User Flow

1. The user opens the WeChat-side entry.
2. The user sends a venting or late-night emotional message.
3. The backend receives the message and identifies the user.
4. The agent checks topic, mood, risk level, and known user preferences.
5. The agent replies in the "late-night sharp-tongued friend" voice.
6. The system stores useful lightweight memory only when appropriate.
7. The admin can review users, adjust personality settings, and manage memory behavior.

## Main Components

### WeChat Entry

The first build should use Enterprise WeChat or a WeChat customer-service style entry. This avoids the stability and account-risk issues of personal WeChat automation while keeping the experience close to a WeChat conversation.

### Conversation Backend

The backend receives inbound messages, routes them to the AI model, applies memory, enforces safety rules, and sends replies back through the WeChat-side channel.

### Personality Engine

The personality engine holds the core prompt, tone limits, example style, and fallback behavior. It should support small adjustments per user, such as softer or sharper tone.

### Memory Layer

The memory layer stores lightweight user preferences and recurring context. It should not store everything by default. The user or admin should be able to turn memory off or clear memory.

### Safety Layer

The safety layer detects severe emotional distress, self-harm language, violent intent, illegal plans, or other high-risk content. In those cases, the AI should stop joking and respond with a more serious, grounding style.

### Admin Console

The admin console should let the owner see invited users, configure personality, manage memory settings, inspect system status, and view concise conversation summaries when needed for troubleshooting.

## Data Flow

1. User message arrives from the WeChat-side channel.
2. The system verifies the source and maps the sender to an internal user record.
3. The message is analyzed for topic, emotional state, and risk.
4. Relevant memory is retrieved if memory is enabled.
5. The AI response is generated using the personality and safety rules.
6. The response is sent back to the WeChat-side channel.
7. Minimal logs and memory updates are stored.

## Error Handling

- If the WeChat callback fails, the system should retry or mark the message as failed.
- If the AI model fails, the user should receive a short, natural fallback message.
- If memory lookup fails, the conversation should continue without memory.
- If risk detection is uncertain, the system should choose the safer serious tone.

## Testing Expectations

The first testable milestone is not implementation. It is a web static prototype that shows the intended pages, flow, and information placement. After the prototype is confirmed, implementation testing should cover:

- Normal venting conversation.
- Late-night emo conversation.
- Work, relationship, and interpersonal complaints.
- User memory creation and use.
- Memory disabled behavior.
- Safety fallback behavior.
- Admin changes to personality settings.
- WeChat message receive/send path.

## Scope Boundaries

The MVP should not include payment, public registration, personal WeChat automation, medical diagnosis, therapy claims, voice chat, image chat, or a large public community.

## Next Stage

Create a web static prototype for:

- WeChat-side chat experience.
- Admin dashboard.
- Personality configuration.
- User and memory management.
- Safety rule overview.

The user must confirm the prototype before formal implementation planning begins.

