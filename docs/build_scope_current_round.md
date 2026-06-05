# Build Scope Current Round

## Build Round 1

| Field | Content |
|---|---|
| Round name | Local companion simulator and admin foundation |
| Product goal | Let the owner try the AI companion flow locally before real WeChat integration |
| Recommended scope | Build the runnable app shell, admin foundation, local chat simulator, safety baseline, memory controls, personality response planning, and multimodal intent stubs |
| Confirmation needed | Yes |
| After confirmation | Start implementation with the project scaffold |

## What Will Be Built Now

| Area | What this means for the product | Expected output |
|---|---|---|
| Runnable local app foundation | The product has a real app base instead of only static prototype files | App scaffold, run command, basic health check |
| Database schema | Users, whitelist state, memory, message metadata, sample-source status, and audit events have a place to live | SQLite-ready schema or migrations |
| Admin console shell | The confirmed prototype turns into real navigable pages | Admin layout, navigation, empty states |
| Users and whitelist | You can control who is allowed into the inner test | User list and allowlist controls |
| Local conversation simulator | You can test chat behavior without WeChat credentials | Local chat page with send/receive simulation |
| Safety Guard baseline | Risky messages do not get playful teasing, stickers, or voice | Safety mode rules and basic tests |
| Memory Service baseline | The agent can remember light preferences and can forget on command | Memory read/write/clear controls |
| Personality response planner | The agent can plan replies in the "嘴欠但靠谱的深夜损友" style | Response plan output with tone, intent, and boundaries |
| Multimodal decision stub | The system can decide when to use text, sticker intent, voice script, or safety response | Mode decision labels and fallback behavior |
| Public sample status panel | Public-source distillation work is visible without downloading large files | Source status UI/API |
| Media asset fallback | Sticker and voice intent can exist before real media files are ready | Media registry stub and text fallback |

## What Will Not Be Built Now

| Excluded item | Why it waits |
|---|---|
| Real WeChat message send/receive | Needs current official API review, credentials, callback configuration, and media capability checks |
| Personal WeChat automation | Not part of the confirmed MVP route because of stability and account-risk concerns |
| Real sticker package downloads | User asked to defer large media downloads until VPN is off, and rights still need review |
| Real voice generation provider integration | Voice provider, cost, latency, and content safety need a separate decision |
| Production deployment | First round should prove the local core flow before deployment work |
| Multi-user public launch | MVP remains owner plus a few friends after the core flow is stable |
| Full model fine-tuning | First round uses behavior rules, prompts, and synthetic/public-source metadata rather than training a model |

## What The User Can Verify After This Round

| Testable flow | Expected result |
|---|---|
| Open the local app | Admin console and simulator are reachable |
| Add or view an inner-test user | Whitelist state is visible and editable |
| Send a normal venting message in the simulator | The agent returns a planned reply in the confirmed personality |
| Send an emotional or risky message | Safety mode activates and playful behavior is disabled |
| Trigger sticker or voice intent | The UI shows sticker/voice intent and falls back to text when no asset exists |
| Save and clear a memory item | Memory can be read, disabled, and cleared |
| View public sample status | Sources show license/download/readiness states without large media downloads |

## Behind The Scenes

| Work | Why it matters |
|---|---|
| Keep modules separated inside one app | Future WeChat, media, memory, and model changes stay easier to replace |
| Use local simulation before platform integration | The personality and safety experience can be tested without waiting for WeChat setup |
| Store decisions and message metadata early | Later debugging and user testing will be less blind |
| Make media optional from day one | Missing sticker or voice assets will not break the chat flow |

## Acceptance Gate

Build Round 1 should be considered ready to start when the user confirms this scope.

Build Round 1 should be considered ready for owner testing only when the local app runs and the simulator can show normal reply, safety reply, memory behavior, and multimodal intent fallback.

## Current User Action

Review this scope. If it feels right, confirm Build Round 1 so implementation can start.
