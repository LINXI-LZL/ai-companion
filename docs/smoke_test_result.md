# Owner Smoke Test Result

## Summary

| Field | Content |
|---|---|
| Build | Build Round 1 local companion simulator |
| URL | `http://127.0.0.1:8765` |
| Date | 2026-06-05 |
| Result | Passed after one display-language fix |
| Remaining action | Review `docs/acceptance_checklist.md` and decide the next build-round focus |

## Observed Flows

| Flow | Evidence | Result |
|---|---|---|
| Open local console | User used the local browser at `http://127.0.0.1:8765` | Passed |
| Normal rant | User reported steps 1-4 were executed before status screenshots | Passed, no blocking issue reported |
| Sleepy voice intent | User reported steps 1-4 were executed before status screenshots | Passed, no blocking issue reported |
| Safety mode | User reported steps 1-4 were executed before status screenshots | Passed, no blocking issue reported |
| Memory | User reported steps 1-4 were executed before status screenshots | Passed, no blocking issue reported |
| Sample status | Screenshot showed 13 public sources visible | Passed after display wording fix |
| Run status | Screenshot showed service running, database path, and deferred media assets | Passed after display wording fix |
| WeChat entry mock | Screenshot showed `wecom_kf`, content type `文字`, mode `文字加表情意图`, send policy `仅本地模拟`, and outbound text | Passed |

## Issue Found And Fixed

| Issue | Impact | Resolution |
|---|---|---|
| Sample Status and Run Status exposed raw English labels such as `metadata_now_dataset_later`, `deferred`, and English media notes | Functional flow worked, but it was unfriendly for nontechnical owner testing | Fixed by localizing visible labels and status descriptions in commit `b016199` |

## Deferred Items

These remain outside Build Round 1 and should not count as smoke-test failures:

| Deferred item | Reason |
|---|---|
| Real credentialed WeChat send/receive | Current WeChat Entry is local simulation only |
| Real sticker package files | Rights review and large downloads are deferred |
| Real voice synthesis | Voice provider choice is not made yet |
| Production deployment | Local validation comes first |

## Next Decision

After reviewing the acceptance checklist, choose the next build-round focus:

| Option | Meaning |
|---|---|
| Real WeChat credentials | Start current Tencent API review and credential setup |
| Real media assets | Prepare approved sticker assets and voice-provider decision |
| Personality quality | Improve reply diversity, emotional nuance, and inner-test scenarios |
