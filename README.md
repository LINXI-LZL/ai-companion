# 微信树洞 AI

这是一个微信风格的 AI 陪聊智能体本地 MVP 项目。目标是让 AI 像一个可以接住吐槽、记住轻量上下文、并能接入企业微信客服的“微信好友”。

## 本地运行

使用 Codex 自带的 Python 运行环境启动服务：

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m app.server --port 8765
```

启动后打开：

```text
http://127.0.0.1:8765
```

当前版本包含：

- 本地聊天模拟器
- 内测用户白名单
- 自动轻量记忆链路
- 公开样本蒸馏状态展示
- 表情包与语音意图兜底
- 安全模式回复
- OpenAI、DeepSeek、Gemini、Dify 外部模型路由
- 企业微信回调 URL 验证
- 企业微信加密文本回调接收
- 企业微信客服真实文本消息拉取与发送

真实表情包素材下载、媒体上传和真实语音合成仍属于后续增强项。

## 可选外部模型

项目默认使用本地回复，不需要付费 API key。如果想接入外部模型，可以在启动服务前设置环境变量。

OpenAI 示例：

```powershell
$env:COMPANION_LLM_PROVIDER='auto'
$env:OPENAI_API_KEY='your-openai-key'
$env:OPENAI_MODEL='gpt-4o-mini'
```

Dify 示例：

```powershell
$env:COMPANION_LLM_PROVIDER='dify'
$env:DIFY_API_KEY='your-dify-key'
$env:DIFY_API_BASE_URL='https://api.dify.ai/v1'
$env:DIFY_RESPONSE_MODE='blocking'
$env:DIFY_APP_USER_PREFIX='wechat-treehole'
```

支持的模型模式：

```text
local | auto | openai | deepseek | gemini | dify
```

Dify 通过 Chat App 的 `/chat-messages` API 接入。应用会把本地场景、记忆、最近历史和兜底回复结构化传给 Dify，但安全判断和本地兜底仍由本项目控制。

运行状态页会展示外部模型是否已配置，但不会显示 API key。

## 企业微信客服回调

启动服务前先设置以下环境变量。前四项用于回调 URL 验证和加密回调 ACK：

```bash
export WECOM_CORP_ID='ww-your-corp-id'
export WECOM_KF_TOKEN='your-callback-token'
export WECOM_KF_ENCODING_AES_KEY='your-43-char-encoding-aes-key'
export WECOM_CALLBACK_PUBLIC_URL='https://ai.ascleet.xyz/api/wecom-live/callback'
```

如果要拉取真实微信客服消息正文并发送真实文本回复，还需要配置 `WECOM_KF_SECRET`。如果能拿到 `WECOM_OPEN_KFID`，也建议配置，它会优先用于出站发送：

```bash
export WECOM_KF_SECRET='your-wecom-kf-secret'
export WECOM_OPEN_KFID='wkf-your-open-kfid'
```

企业微信后台填写的回调地址格式：

```text
https://your-public-domain/api/wecom-live/callback
```

本地服务支持：

- 验证企业微信加密 `echostr`
- 快速 ACK 加密回调
- 将回调任务入队
- 后台异步调用微信客服 `sync_msg`
- 按 `msgid` 去重，避免企业微信重试或旧消息批量返回导致重复回复
- 在配置 `WECOM_KF_SECRET` 和 `open_kfid` 后调用 `send_msg` 发送真实文本回复

如果发送 API 失败，回调仍会返回 `success`，并记录不包含密钥的安全审计日志。

验收步骤见：

```text
docs/wecom_real_callback_smoke_test.md
```

## 测试

运行完整测试：

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -q
```
