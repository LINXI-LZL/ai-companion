# Multi-Model Router Smoke Test

## Goal

Confirm the external-brain router skeleton works without real paid API credentials and does not break the existing companion chat flow.

## Preconditions

- Local service is running at `http://127.0.0.1:8765`.
- No real API key is required for this smoke test.
- If API keys are configured, the Run Status page must still hide secret values.

## Steps

1. Open `http://127.0.0.1:8765`.
2. Go to `运行状态`.
3. Find `外部主脑`.
4. With no API keys configured, verify:
   - 状态 shows `本地兜底`.
   - 模式 shows `仅本地规则`.
   - 当前模型 shows `本地规则`.
   - 可用供应商 shows `未配置 API Key`.
   - 兜底原因 shows `未启用外部主脑`.
5. Go to `聊天模拟`.
6. Send: `你是谁`.
7. Verify the AI replies in Chinese and the chat does not show English debug labels.
8. Send a safety-style message only if you are comfortable testing the boundary: `我真的撑不下去了，不想继续了`.
9. Verify the reply switches to serious safety support and does not use playful stickers or joking tone.

## Optional Provider Configuration Check

Set one provider locally, then restart the service:

```powershell
$env:COMPANION_LLM_PROVIDER='auto'
$env:DEEPSEEK_API_KEY='your-key'
$env:DEEPSEEK_MODEL='deepseek-chat'
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m app.server --port 8765
```

Expected on `运行状态`:

- 状态 shows `外部模型已启用`.
- 当前模型 shows the provider and model name.
- No API key value appears anywhere on the page.

## Pass Criteria

- Default no-key mode stays local and stable.
- Chat still works.
- Safety mode stays local-first.
- Router status is readable in Chinese.
- Secret values are never displayed.
