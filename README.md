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

Real WeChat integration, real sticker assets, and real voice synthesis are intentionally deferred.

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

## Test

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```
