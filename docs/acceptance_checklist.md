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
| Can the owner use the local simulator to judge the personality direction? | To review |
| Is the safety behavior acceptable for inner testing? | To review |
| Is the admin console clear enough for the owner to operate? | To review |
| Is the product ready to invite one or two friends for local-style feedback? | To review |
| Should the next build round focus on real WeChat credentials, real media assets, or personality quality? | To decide |
