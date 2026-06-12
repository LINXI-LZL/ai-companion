# WeCom Real Callback Result

## Status

Ready for owner smoke test with quick ACK, async processing, dedupe, and real text send.

## Implemented

| Area | Result |
|---|---|
| AES support | Added local AES-256-CBC encrypt/decrypt compatible with the Enterprise WeChat callback packaging format |
| URL verification | Valid signed `echostr` can be decrypted and returned as plain text |
| Encrypted POST callback | Encrypted XML can be decrypted, parsed, normalized, deduped, and queued |
| Failure audit | Failed callback parsing now records safe audit fields: `status`, `http_status`, `signature_valid`, `body_has_encrypt`, and body length |
| Quick ACK | Real callback POST returns `success` after queueing instead of waiting for `sync_msg` or `send_msg` |
| Background worker | Queued jobs are processed by a daemon worker started with the local server |
| Callback dedupe | Repeated callback delivery reuses the first job and writes `wecom_live_callback_duplicate` |
| Message dedupe | Repeated `sync_msg` message IDs write `wecom_live_message_duplicate` and do not send twice |
| Real customer-service event | Worker calls WeCom Customer Service `sync_msg` for `kf_msg_or_event` when `WECOM_KF_SECRET` is configured |
| Text body pull | Text messages returned by `sync_msg` enter the companion flow and generate replies |
| Real text send | Worker sends generated text replies through WeCom Customer Service `send_msg` when `WECOM_KF_SECRET` and `open_kfid` are available |
| Send failure audit | Send API failures still ACK `success` and record safe `wecom_live_send_msg_failure` audit events |
| Admin status | `/api/wecom-live/status` reports `ready_for_real_callback` and redacts secrets |
| Callback field split | URL verification no longer requires `WECOM_KF_SECRET` or `WECOM_OPEN_KFID` |
| Safety boundary | Text send is supported; stickers, voice, image, and other media sends remain deferred |

## Verification

- `tests.test_wechat_adapter` covers AES-CBC known-vector encryption/decryption.
- URL verification decrypts encrypted `echostr`.
- Encrypted POST direct text callback queues immediately, then the worker enters the existing companion flow.
- Encrypted POST direct text callback worker can call `send_msg` and records a safe success/failure audit.
- Encrypted `kf_msg_or_event` callback queues immediately; the worker can pull text bodies through `sync_msg`, enter the companion flow, and call `send_msg`.
- Duplicate callbacks do not enqueue duplicate jobs.
- Duplicate synced message IDs do not send duplicate replies.
- Namespaced/form-wrapped callback XML can still expose `Encrypt`.
- Missing `Encrypt` and unsupported customer-service pull events are audited without logging keys or raw bodies.
- Existing local mock and dev inbound paths remain covered.
- Full suite: 90 tests passed.

## Owner Smoke Test

Use `docs/wecom_real_callback_smoke_test.md`.

The key check is whether Enterprise WeChat accepts the public callback URL. `127.0.0.1` cannot be used directly by Enterprise WeChat, so a public HTTPS URL or tunnel is still required for real platform verification.

## Deferred

- Cursor persistence for multi-page `sync_msg` pulls.
- Public HTTPS deployment or tunnel automation.
- Sticker and voice media upload.
