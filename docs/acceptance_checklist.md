# Acceptance Checklist

## Build Round 1 Acceptance

Use this checklist after running the local smoke test. Mark an item as pass only when you have seen it work in the local app.

| Area | Pass Criteria | Status |
|---|---|---|
| Local app opens | `http://127.0.0.1:8765` opens without browser or server error | Pass |
| Main navigation | 聊天模拟、用户、记忆、微信入口、样本状态、运行状态 are visible and clickable | Pass |
| Normal rant reply | A work-rant message gets a relevant sharp-but-supportive reply | Pass |
| No repeated generic answer | Repeating the same user question does not return the exact same reply forever | Automated pass |
| Sticker intent | Suitable messages show sticker intent while falling back to text | Pass |
| Sleepy voice intent | Sleepy late-night messages show voice intent and a voice script | Pass |
| Safety mode | High-risk messages switch to serious support and disable playful sticker/voice behavior | Pass |
| Memory | A light memory such as `用户喜欢短回复` can be saved, used, and cleared | Pass |
| WeChat entry mock | The 微信入口 tab can simulate inbound text and show an outbound envelope | Pass |
| Public source status | 样本状态 shows source names, license, download policy, and readiness status | Pass after wording fix |
| Run status | 运行状态 shows service status, database path, and deferred media assets | Pass after wording fix |

## MVP Pass Bar

| Level | Meaning |
|---|---|
| Pass | All core local flows work, and any remaining problems are only wording polish or deferred real integrations |
| Conditional pass | Core chat works, but one noncritical admin/status view or wording area needs repair before sharing with friends |
| Fail | Chat sending, safety mode, memory, or WeChat Entry mock cannot be tested reliably |

## Known Deferred Items

These items should not block Build Round 1 acceptance:

| Deferred item | Why it does not block this round |
|---|---|
| Real WeChat credentials | This round validates the local product flow and adapter contract first |
| Real sticker files | Current version stores sticker intent and uses text fallback |
| Real voice synthesis | Current version stores voice intent and script only |
| Production deployment | Local validation comes before deployment |
| Full fine-tuning | Current behavior is rule/prompt based with public-source planning |

## Acceptance Decision

| Question | Decision |
|---|---|
| Can the owner use the local simulator to judge the personality direction? | Pass |
| Is the safety behavior acceptable for inner testing? | Pass |
| Is the admin console clear enough for the owner to operate? | Pass after status-page wording fix |
| Is the product ready to invite one or two friends for local-style feedback? | Pass for local-style feedback |
| Should the next build round focus on real WeChat credentials, real media assets, or personality quality? | To decide |

## Final Round 1 Decision

| Field | Decision |
|---|---|
| Owner decision | 第一轮通过 |
| Decision date | 2026-06-05 |
| Acceptance level | Pass |
| Notes | Build Round 1 local simulator and admin foundation are accepted. Real WeChat send/receive, real sticker files, real voice synthesis, and deployment remain next-round decisions. |

## Build Round 2 Personality Quality Acceptance

| Area | Pass Criteria | Status |
|---|---|---|
| Chosen style | Personality route is `刀子嘴豆腐心`: sharp, teasing, and still on the user's side | Implemented |
| Work-rant variation | Ten similar work rants do not produce identical answers | Automated pass |
| Scenario memory feel | Repeated work themes include a sense that the same kind of issue has returned | Automated pass |
| Self-blame boundary | Self-blame replies separate the user from the problem and avoid attacking the user | Automated pass |
| Safety override | High-risk messages suppress playful or biting tone | Automated pass |
| Existing MVP behavior | Safety, memory prefix, sticker intent, voice script, WeChat mock, and status pages keep working | Automated pass |

## Build Round 2 Owner Test

| Field | Value |
|---|---|
| Smoke test script | `docs/personality_round_2_smoke_test.md` |
| Current owner action | Run the personality smoke test in `聊天模拟` |
| Acceptance level | Ready for owner test |
