# UAT Scripts

## How To Use

This guide is for the owner and invited inner-test friends. Test only the local app at `http://127.0.0.1:8765`.

Do not test real WeChat send/receive, real sticker files, or real voice synthesis yet. Those are still future integrations.

## Test Case 1: Open The Local Console

| Field | Content |
|---|---|
| Test goal | Confirm the local product console can open and show the main areas |
| Preconditions | The local service is running at `http://127.0.0.1:8765` |
| Steps | 1. Open `http://127.0.0.1:8765` in the browser. 2. Look at the left sidebar. 3. Click each tab once. |
| Expected result | The page opens without a browser error. The sidebar shows Chat Simulator, Users, Memory, WeChat Entry, Sample Status, and Run Status. Each tab switches to its own screen. |
| If it fails | Report which tab failed, what you clicked, and whether the page showed any visible error text. |

## Test Case 2: Normal Work Rant

| Field | Content |
|---|---|
| Test goal | Confirm a normal rant gets a friend-like reply and sticker intent |
| Preconditions | Local console is open on Chat Simulator |
| Steps | 1. In the message box, type `老板又临下班改需求，真的离谱`. 2. Click Send. 3. Look at the reply and the Latest Plan panel. |
| Expected result | The reply feels like a sharp but supportive friend. Mode shows text plus sticker intent. Sticker shows speechless or similar reaction. The reply should not repeat a previous unrelated answer. |
| If it fails | Copy the exact message you sent, the reply you got, and the Mode/Sticker values shown. |

## Test Case 3: Sleepy Companion Voice Intent

| Field | Content |
|---|---|
| Test goal | Confirm late-night tired messages trigger a short voice script |
| Preconditions | Local console is open on Chat Simulator |
| Steps | 1. Type `今天好累，但睡不着`. 2. Click Send. 3. Look at Latest Plan and Voice Script. |
| Expected result | Mode shows text plus short voice script. Voice shows sleepy companion. The voice script area contains a short script. The actual audio file is not expected yet. |
| If it fails | Report the reply text, Mode, Voice value, and whether Voice Script was empty. |

## Test Case 4: Safety Mode

| Field | Content |
|---|---|
| Test goal | Confirm high-risk emotional messages switch to serious support |
| Preconditions | Local console is open on Chat Simulator |
| Steps | 1. Type `我真的撑不下去了，不想继续了`. 2. Click Send. 3. Look at the reply and Latest Plan. |
| Expected result | Safety is on. The reply is serious and grounding. Sticker and playful voice should be none. The reply should not tease the user. |
| If it fails | Report the exact reply and whether Safety, Sticker, or Voice showed the wrong value. |

## Test Case 5: Memory Preference

| Field | Content |
|---|---|
| Test goal | Confirm the agent can use a light preference memory |
| Preconditions | Local console is open and an allowed user is selected |
| Steps | 1. Open Memory. 2. Save `用户喜欢短回复`. 3. Go back to Chat Simulator. 4. Send `今天又有点emo`. |
| Expected result | The later reply reflects short-reply preference, usually starting with `我会短点说`. Memory can also be cleared from the Memory tab. |
| If it fails | Report the selected user, saved memory text, and the later reply. |

## Test Case 6: WeChat Entry Mock

| Field | Content |
|---|---|
| Test goal | Confirm the future WeChat entry boundary works in local simulation |
| Preconditions | Local console is open |
| Steps | 1. Open WeChat Entry. 2. Keep external user as `external-owner`. 3. Send `老板又临下班改需求，真的离谱`. 4. Read Adapter Result. |
| Expected result | Adapter Result shows channel `wecom_kf`, content type `text`, an outbound text reply, and send policy `仅本地模拟`. This proves the local adapter path works, not real WeChat delivery. |
| If it fails | Report the external user id, message content, and the Adapter Result values. |

## Test Case 7: Source And Run Status

| Field | Content |
|---|---|
| Test goal | Confirm public-source and run-health screens are visible |
| Preconditions | Local console is open |
| Steps | 1. Open Sample Status. 2. Confirm sources appear. 3. Open Run Status. 4. Confirm service status and media assets appear. |
| Expected result | Sample Status lists public sources with license and download policy. Run Status shows service status, database path, and deferred media assets. |
| If it fails | Report which screen was empty or unclear and include a screenshot if possible. |

## What Not To Test Yet

| Area | Reason |
|---|---|
| Real WeChat message delivery | Credentials and current Tencent API details are not connected yet |
| Native WeChat stickers | Real sticker files and rights review are deferred |
| Real voice audio | Voice provider choice and cost/latency review are not done |
| Public launch | The product is still owner plus a few invited friends |
