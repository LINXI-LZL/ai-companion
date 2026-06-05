# Personality Quality Round 2 Design

## Decision

Build Round 2 focuses on personality quality. The chosen style is `刀子嘴豆腐心`: the companion may be sharp, teasing, and funny, but it must end up on the user's side.

## Product Goal

Make the local chat feel less like a fixed script and more like a real late-night friend who remembers the conversation rhythm, reacts to repeated themes, and keeps emotional safety boundaries.

## Scope

This round improves text behavior only. Real WeChat credentials, real sticker files, real voice synthesis, deployment, and large public dataset downloads remain deferred.

## Behavior Rules

1. A normal low-risk reply should usually contain three beats: acknowledge the feeling, make one playful jab at the situation, then offer a small next step or follow-up question.
2. The jab targets the situation, task, boss, timing, or user's inner drama. It must not attack the user's body, identity, intelligence, worth, or personality.
3. Similar repeated themes should vary across turns. The companion should sound like it remembers that the topic has come back.
4. High-risk messages must bypass the playful style and use serious safety support.
5. Lightweight memory such as `用户喜欢短回复` still applies.

## First Scenario Pack

The first upgraded pack covers:

- boss and work rants
- procrastination
- self-blame
- missing someone or wanting the companion
- boredom
- late-night emo
- friendship or relationship friction
- greeting and identity checks
- generic fallback

## Acceptance Criteria

- Ten similar low-risk work rants do not produce ten identical answers.
- Self-blame replies explicitly separate the user from the problem.
- High-risk replies do not use teasing, sticker-style banter, or playful escalation.
- Existing Build Round 1 behavior stays intact: safety, memory prefix, sticker intent, voice script, WeChat mock, and status pages.

## Implementation Shape

Keep the change small. Upgrade `app/orchestrator.py` with scenario detection, scenario-level turn counting, and a compact reply library. Keep `app/multimodal.py`, `app/safety.py`, storage, and frontend contracts stable unless a test shows a real need to change them.
