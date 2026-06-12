# WeCom Real Callback Design

## Product Goal

Move the Enterprise WeChat route from a configuration skeleton to a real callback receive path: the platform can verify the callback URL and encrypted text events can enter the companion engine.

## Scope

This round implements:

- `echostr` decryption for Enterprise WeChat URL verification.
- Encrypted POST XML callback parsing.
- Signature verification before decrypting callback payloads.
- Text event normalization into the existing `wecom_live` inbound envelope.
- `success` ACK for real callback POST requests.
- Status API wording that shows whether real callback verification is ready.

## Non-Goals

- No real outbound request to Enterprise WeChat send APIs.
- No access-token cache.
- No public HTTPS deployment automation.
- No sticker or voice media upload.

## Data Flow

1. Enterprise WeChat sends GET `/api/wecom-live/callback` with `msg_signature`, `timestamp`, `nonce`, and encrypted `echostr`.
2. The service verifies the SHA1 signature using `WECOM_KF_TOKEN`.
3. The service decrypts `echostr` using `WECOM_KF_ENCODING_AES_KEY`, validates `WECOM_CORP_ID`, and returns the plaintext.
4. Enterprise WeChat sends encrypted POST XML callbacks to the same endpoint.
5. The service verifies, decrypts, parses XML, normalizes text content, runs the companion flow, records local data, builds an outbound payload, and replies `success`.

## Security Boundaries

- Secrets are read only from environment variables.
- Status output reports only `set`, `missing`, or readiness labels.
- Invalid signatures are rejected before decryption.
- CorpID mismatch is treated as a failed callback.
- Outbound network sending remains disabled.

## Acceptance Criteria

- AES-256-CBC core passes a known NIST vector.
- Valid encrypted `echostr` returns plaintext with HTTP 200.
- Invalid signed ciphertext returns a clear error.
- Encrypted text callback routes into the companion flow and returns `success`.
- The admin status labels are understandable to a nontechnical owner.
