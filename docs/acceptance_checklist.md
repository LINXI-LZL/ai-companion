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
| Current owner action | none |
| Acceptance level | Pass |

## Final Round 2 Decision

| Field | Decision |
|---|---|
| Owner decision | 第二轮通过 |
| Decision date | 2026-06-05 |
| Acceptance level | Pass |
| Notes | Build Round 2 `刀子嘴豆腐心` personality upgrade is accepted. Real WeChat send/receive, real sticker files, real voice synthesis, and wider friend testing remain next-round choices. |

## Build Round 3 WeCom Live Route Acceptance

| Area | Pass Criteria | Status |
|---|---|---|
| Live config self-check | Admin can see whether required WeCom credential fields are present without exposing secret values | Automated pass |
| Signature check | SHA1 signature uses sorted Token, timestamp, nonce, and encrypted string | Automated pass |
| Callback boundary | Valid signed callback GET returns a clear `crypto_not_configured` state until official crypto support is added | Automated pass |
| Dev live inbound | Plaintext/dev `wecom_live` events route through the companion engine | Automated pass |
| Send payload | Text send envelope includes `touser`, `open_kfid`, `msgtype`, and `text.content` | Automated pass |
| Local mock preservation | Existing local WeChat mock keeps working | Automated pass |

## Build Round 3 Owner Test

| Field | Value |
|---|---|
| Smoke test script | `docs/wecom_live_round_3_smoke_test.md` |
| Current owner action | Run the WeCom live route smoke test in `微信入口` |
| Acceptance level | Ready for owner test |

## Auto Memory Polish Acceptance

| Area | Pass Criteria | Status |
|---|---|---|
| Automatic preference memory | A preference such as `以后跟我说短点` saves `用户喜欢短回复` automatically | Automated pass |
| Automatic repeated-theme memory | Repeated work rants save one work-pressure memory without duplicates | Automated pass |
| Sensitive suppression | Phone numbers, tokens, secrets, and credential-like content are not saved, even if the user says to remember them | Automated pass |
| High-risk suppression | High-risk self-harm wording is not saved as memory, even when phrased as an explicit remember request | Automated pass |
| Memory page copy | The Memory page reads as automatic memory management, not manual data entry | Automated pass |

## Auto Memory Owner Test

| Field | Value |
|---|---|
| Smoke test script | `docs/auto_memory_smoke_test.md` |
| Current owner action | none |
| Acceptance level | Pass |

## Final Auto Memory Decision

| Field | Decision |
|---|---|
| Owner decision | 验收通过 |
| Decision date | 2026-06-05 |
| Acceptance level | Pass |
| Notes | Automatic lightweight memory is accepted. The agent now auto-saves safe stable preferences and repeated themes, while skipping sensitive or high-risk content. |

## Expression Logic Polish Acceptance

| Area | Pass Criteria | Status |
|---|---|---|
| Generic poetic message | Ambiguous/poetic messages are acknowledged directly without `同类剧情` or life-coaching suffixes | Automated pass |
| AI quality feedback | Feedback such as `我觉得你不太智能` gets a direct repair reply instead of generic coaching | Automated pass |
| Scenario-specific repetition | Repeated-theme notes only appear in meaningful scenarios such as work, identity checks, self-blame, or sleep | Automated pass |
| Existing personality | Work-rant replies still keep `刀子嘴豆腐心` shape | Automated pass |

## Expression Logic Owner Test

| Field | Value |
|---|---|
| Smoke test script | `docs/expression_logic_smoke_test.md` |
| Current owner action | Run the expression logic smoke test in `聊天模拟` |
| Acceptance level | Ready for owner test |
