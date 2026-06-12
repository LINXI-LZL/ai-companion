# WeCom Real Callback Smoke Test

## Goal

Verify that the local service can complete Enterprise WeChat callback URL verification, decrypt encrypted text callbacks, pull real customer-service text bodies, and send text replies back through WeCom Customer Service.

## What This Round Supports

- GET `/api/wecom-live/callback` URL verification with `msg_signature`, `timestamp`, `nonce`, and encrypted `echostr`.
- POST `/api/wecom-live/callback` encrypted XML event parsing.
- Text message normalization into the existing companion chat flow.
- Fast `success` ACK to Enterprise WeChat after decrypting and enqueueing the callback.
- A background worker processes queued callbacks, calls `sync_msg` for `kf_msg_or_event`, and sends text replies through `send_msg`.
- Callback-level dedupe prevents Enterprise WeChat retries from creating duplicate jobs.
- Message-level dedupe prevents repeated `sync_msg` payloads from sending duplicate replies for the same WeCom `msgid`.
- Safe send audit events without logging `Secret`, `access_token`, callback Token, EncodingAESKey, or reply text.

## Still Deferred

- Public HTTPS hosting or tunnel setup.
- Cursor persistence for multi-page `sync_msg` pulls.
- Sticker and voice media upload.

## Required Environment Variables

For URL verification and encrypted callback receive, these are required:

```bash
export WECOM_CORP_ID='ww-your-corp-id'
export WECOM_KF_TOKEN='your-callback-token'
export WECOM_KF_ENCODING_AES_KEY='your-43-char-encoding-aes-key'
export WECOM_CALLBACK_PUBLIC_URL='https://ai.ascleet.xyz/api/wecom-live/callback'
```

These are optional for URL verification, but `WECOM_KF_SECRET` is required to pull real text bodies with `sync_msg` and send text replies with `send_msg`. `WECOM_OPEN_KFID` is preferred when available:

```bash
export WECOM_KF_SECRET='your-wecom-kf-secret'
export WECOM_OPEN_KFID='wkf-your-open-kfid'
```

Then start:

```bash
python3 -m app.server --port 8765
```

## Step 1: Check Local Readiness

Open:

```text
http://127.0.0.1:8765/api/wecom-live/status
```

Expected:

- `configured` is `true`.
- `ready_for_real_callback` is `true`.
- `crypto_status` is `ready`.
- `send_mode` is `real_text_send`.
- No secret value is printed.

If `configured` is `false` but `ready_for_real_callback` is `true`, URL verification can still proceed. That means callback credentials are ready, but `WECOM_KF_SECRET` or `WECOM_OPEN_KFID` is still missing for real text send.

## Step 2: Configure Enterprise WeChat Callback

In the Enterprise WeChat / WeChat Customer Service callback settings, use:

| Field | Value |
|---|---|
| URL | Your public HTTPS URL ending with `/api/wecom-live/callback` |
| Token | Same as `WECOM_KF_TOKEN` |
| EncodingAESKey | Same as `WECOM_KF_ENCODING_AES_KEY` |

Do not use `127.0.0.1` as the Enterprise WeChat callback URL. Enterprise WeChat must reach a public HTTPS address.

## Step 3: URL Verification

Click the platform's save/verify button.

Expected:

- Enterprise WeChat accepts the URL.
- Local service returns the decrypted `echostr` as plain text.
- If verification fails, check the status API first, then check whether the public URL forwards to local port `8765`.

## Step 4: Text Callback

Send a text message from the Enterprise WeChat customer-service entry.

Expected:

- The callback receives encrypted XML.
- The service returns `success` quickly after writing a queued job.
- The callback writes `wecom_live_callback_queued`; duplicate callbacks write `wecom_live_callback_duplicate` and still return `success`.
- The background worker writes `wecom_live_job_started` and `wecom_live_job_done` around real processing.
- If the callback contains direct text `Content`, the worker records the user and companion reply, then sends text through `send_msg`.
- If the callback is `kf_msg_or_event` and `WECOM_KF_SECRET` is configured, the worker calls `sync_msg`, pulls text messages, records the user and companion reply, sends the reply through `send_msg`, and writes a `wecom_live_sync_msg_processed` audit event.
- Successful sends write `wecom_live_send_msg_success` with safe metadata such as `msgid_present`, `open_kfid`, and `msgtype`.
- Failed sends still return `success` to Enterprise WeChat and write `wecom_live_send_msg_failure`.
- If `WECOM_KF_SECRET` is missing, the service still returns `success` and writes `wecom_live_sync_msg_deferred`.
- Duplicate synced messages write `wecom_live_message_duplicate` and are not sent again.

## Common Failures

| Symptom | Meaning | Fix |
|---|---|---|
| `config_missing` | Required env vars are missing | Set all `WECOM_*` variables and restart |
| `invalid_encoding_aes_key` | EncodingAESKey format is wrong | Copy the 43-character key again |
| `signature_invalid` | Token, timestamp, nonce, or encrypted payload mismatch | Confirm Token and callback URL query are unchanged |
| `corp_id_mismatch` | Decrypted CorpID differs from env CorpID | Check `WECOM_CORP_ID` |
| `sync_msg_deferred` | Callback arrived but Secret is missing, so body cannot be pulled | Set `WECOM_KF_SECRET` and restart |
| `sync_msg_failed` | WeCom API returned an error or timeout | Check Secret, CorpID, and API permissions |
| `send_msg_failed` | Reply was generated but WeCom send API rejected the send or timed out | Check `WECOM_KF_SECRET`, `WECOM_OPEN_KFID`, customer-service permissions, and whether the user is still in a valid service session |
| Public URL cannot verify | WeCom cannot reach your machine | Use a public HTTPS host or tunnel |
