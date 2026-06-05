# Debug Next Actions

## Current Issue State

| Field | Content |
|---|---|
| Build | Build Round 1 local companion simulator |
| Owner decision | 第一轮通过 |
| Active blocking issues | None |
| Last issue fixed | Status pages showed raw English labels and notes |
| Fix commit | `b016199 Localize status pages after smoke feedback` |

## Issue Ledger

| Issue | Status | Next action |
|---|---|---|
| AI repeated the same answer for repeated questions | Fixed | Covered by automated tests |
| Reply bubbles showed English debug metadata | Fixed | Covered by static UI test |
| Sample Status and Run Status exposed raw English labels | Fixed | Covered by static UI test |
| Real WeChat delivery is not connected | Deferred | Decide in next build round |
| Real sticker and voice files are not connected | Deferred | Decide in next build round |

## Repair Queue

There are no active repair tasks blocking Build Round 1 acceptance.

If new issues appear during friend testing, use `docs/bug_feedback_template.md`, then add each issue here with severity, owner-visible impact, and repair status.
