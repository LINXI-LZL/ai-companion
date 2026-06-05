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

Real WeChat integration, real sticker assets, and real voice synthesis are intentionally deferred.

## Test

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```
