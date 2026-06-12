# 微信树洞 AI

Local MVP workspace for the WeChat-style AI companion product.

## Run Locally

Use the bundled Python runtime in Codex:

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m app.server --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

The Round 1 app includes:

- local chat simulator
- inner-test user whitelist
- lightweight memory controls
- public sample source status
- sticker and voice intent fallback
- safety-mode behavior
- optional external model router for OpenAI, DeepSeek, Gemini, and Dify
- Enterprise WeChat callback verification, encrypted text callback receive path, and real text send path

Real sticker assets, media upload, and real voice synthesis are intentionally deferred.

## Optional External Brain

The app defaults to local replies and does not need paid API keys. To try an external model, set a provider before starting the server:

```powershell
$env:COMPANION_LLM_PROVIDER='auto'
$env:OPENAI_API_KEY='your-openai-key'
$env:OPENAI_MODEL='gpt-4o-mini'
```

```powershell
$env:COMPANION_LLM_PROVIDER='dify'
$env:DIFY_API_KEY='your-dify-key'
$env:DIFY_API_BASE_URL='https://api.dify.ai/v1'
$env:DIFY_RESPONSE_MODE='blocking'
$env:DIFY_APP_USER_PREFIX='wechat-treehole'
```

Supported provider modes:

```text
local | auto | openai | deepseek | gemini | dify
```

Dify is used through its Chat App `/chat-messages` API. The app sends structured local context to Dify, but local safety and local fallback stay in control.

The Run Status page shows provider readiness without displaying API keys.

## Enterprise WeChat Callback

Set these variables before starting the server. The first four are enough for URL verification and encrypted callback ACK:

```bash
export WECOM_CORP_ID='ww-your-corp-id'
export WECOM_KF_TOKEN='your-callback-token'
export WECOM_KF_ENCODING_AES_KEY='your-43-char-encoding-aes-key'
export WECOM_CALLBACK_PUBLIC_URL='https://ai.ascleet.xyz/api/wecom-live/callback'
```

Set `WECOM_KF_SECRET` to pull real WeCom Customer Service text bodies with `sync_msg` and send text replies with `send_msg`. `WECOM_OPEN_KFID` is preferred when available and is used for outbound sending:

```bash
export WECOM_KF_SECRET='your-wecom-kf-secret'
export WECOM_OPEN_KFID='wkf-your-open-kfid'
```

Callback endpoint:

```text
https://your-public-domain/api/wecom-live/callback
```

The local service can verify encrypted `echostr`, ACK encrypted callbacks, enqueue callback work, use a background worker to call WeCom Customer Service `sync_msg`, and send real text replies through `send_msg` when `WECOM_KF_SECRET` and `open_kfid` are available. If the send API fails, the callback still ACKs `success` and records a safe audit event without logging secrets.

See `docs/wecom_real_callback_smoke_test.md` for the owner smoke test.

## Test

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```
