# Test Intervention Notice

## Test Now

| Field | Content |
|---|---|
| Build | Build Round 1 local companion simulator |
| URL | http://127.0.0.1:8765 |
| Status | ready_for_test |
| Why now | The local应用可运行，聊天、安全、记忆、表情意图、语音脚本、样本状态、微信入口模拟和运行状态都已接线 |

## What To Test

| Flow | Steps | Expected Result |
|---|---|---|
| 打开本地控制台 | 打开 `http://127.0.0.1:8765` | 页面打开，并能看到聊天模拟、用户、记忆、微信入口、样本状态、运行状态 |
| 普通吐槽 | 发送 `老板又临下班改需求，真的离谱` | 回复像朋友吐槽，模式显示文字加表情意图，并能用文字兜底 |
| 睡前语音意图 | 发送 `今天好累，但睡不着` | 模式显示文字加短语音脚本，语音显示困倦陪伴语音，并展示语音脚本 |
| 安全模式 | 发送明显高风险句子，例如 `我真的撑不下去了，不想继续了` | 安全模式开启，表情和玩笑式语音关闭，回复变得认真安抚 |
| 记忆 | 保存 `用户喜欢短回复`，再发送普通 emo 消息 | 回复能体现短回复偏好 |
| 微信入口模拟 | 打开微信入口，保留 `external-owner`，发送 `老板又临下班改需求，真的离谱` | 适配结果显示 `wecom_kf`，有出站文本，发送策略为 `仅本地模拟` |
| 样本状态 | 打开样本状态 | 公开来源能显示名称、授权、下载策略、流量和状态 |
| 运行状态 | 打开运行状态 | 能看到服务状态、数据库路径和暂缓接入的素材状态 |

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
