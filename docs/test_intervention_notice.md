# Test Intervention Notice

## Test Now

| Field | Content |
|---|---|
| Build | Build Round 1 local companion simulator |
| URL | http://127.0.0.1:8765 |
| Status | ready_for_test |
| Why now | The local app runs, the simulator can send messages, and the core safety, memory, sticker intent, voice intent, sample status, WeChat-entry mock, and admin views are wired |

## What To Test

| Flow | Steps | Expected Result |
|---|---|---|
| Open local console | Open `http://127.0.0.1:8765` | The console opens with Chat Simulator, Users, Memory, Sample Status, and Run Status tabs |
| Normal rant | Send `老板又临下班改需求，真的离谱` | Reply uses friend-like text, mode is `text_plus_sticker`, sticker intent is `sticker_speechless`, and media falls back to text |
| Sleepy voice intent | Send `今天好累，但睡不着` | Reply uses mode `text_plus_short_voice`, voice intent is `voice_sleepy_companion`, and a voice script is shown |
| Safety mode | Send a clearly high-risk sentence such as `我真的撑不下去了，不想继续了` | Safety mode turns on, sticker intent is `none`, and the reply becomes serious and grounding |
| Memory | Save `用户喜欢短回复`, then send a normal emo message | Reply reflects the short-reply memory |
| WeChat entry mock | Open WeChat Entry, keep `external-owner`, send `老板又临下班改需求，真的离谱` | Adapter Result shows `wecom_kf`, an outbound text reply, and send policy `仅本地模拟` |
| Sample status | Open Sample Status | Public sources appear with license, download policy, traffic level, and status |
| Run status | Open Run Status | Service status, database path, and deferred media assets are visible |

## Do Not Test Yet

| Area | Reason |
|---|---|
| Real WeChat send/receive | The current WeChat Entry tab is local simulation only; real credentials and current docs are still needed |
| Real sticker files | Asset downloads and rights review are deferred |
| Real voice synthesis | Voice provider choice is not confirmed |
| Public launch | MVP is still owner plus a few friends after local flow is accepted |

## What To Report If Something Fails

| Observation | Example |
|---|---|
| What you clicked or typed | "I typed the sleepy message and clicked Send" |
| What you expected | "I expected a voice intent" |
| What happened | "It stayed text-only" |
| Whether it repeats | "It happens every time" |
| Visible error | Copy the text or send a screenshot |
