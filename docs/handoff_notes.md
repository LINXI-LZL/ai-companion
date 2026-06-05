# Handoff Notes

## Current State

Build Round 1 is accepted. The project has a runnable local app, a local WeChat-entry mock, documented test scripts, a completed smoke-test record, and no active blocking repair queue.

The current project gate is choosing the Build Round 2 focus.

## How To Run Locally

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m app.server --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

## How To Verify

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```

Expected result: all tests pass.

## Important Boundaries

| Boundary | Note |
|---|---|
| WeChat Entry | Local simulation only; not real credentialed WeChat delivery |
| Stickers | Intent only; no real sticker package files yet |
| Voice | Script only; no real audio provider yet |
| Memory | Lightweight preferences only; no private chat scraping |
| Public samples | Metadata and seed rules only; large downloads remain deferred |

## Recommended Build Round 2 Options

| Option | Scope | Product impact |
|---|---|---|
| A. Real WeChat credential path | Review current Tencent docs, prepare config, add webhook verification and send/receive adapter | Moves from local simulator toward real channel integration |
| B. Real media path | Add approved sticker files, choose voice provider, keep text fallback | Makes the companion feel more human |
| C. Personality quality path | Add scenario packs, reply variation rules, tone controls, and richer memory preferences | Improves friend-like quality before inviting more testers |

## Recommended Default

Choose C first if you want the inner-test experience to feel good before dealing with platform credentials. Choose A first if your top priority is seeing messages flow through an actual WeChat-side entry.
