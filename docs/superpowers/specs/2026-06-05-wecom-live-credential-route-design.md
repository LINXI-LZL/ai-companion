# WeCom Live Credential Route Design

## Decision

Build Round 3 focuses on the real WeChat/WeCom credential path. The goal is to move from a local mock toward a real Enterprise WeChat / WeChat Customer Service entry without asking the owner to paste real secrets into chat or source code.

## Product Goal

Prepare the product for real WeChat-side receive/send testing by adding configuration checks, callback preflight, live-channel normalization, text-send payload generation, and an admin self-check view.

## Scope

This round builds:

- A `wecom_live` adapter separate from the existing local mock.
- Environment-based configuration discovery for `CorpID`, WeChat Customer Service `Secret`, `Token`, `EncodingAESKey`, and `open_kfid`.
- Signature verification using the Enterprise WeChat token/timestamp/nonce/encrypted-string SHA1 rule.
- A callback endpoint that can preflight GET verification requests and report when AES decryption support is still missing.
- A POST endpoint that accepts plaintext/dev live events and routes them through the existing companion engine.
- A text-send payload builder for the official WeChat Customer Service send-message shape.
- A backend status API and visible admin self-check panel.

## Explicit Non-Goals

- Do not automate a personal WeChat account.
- Do not store real credentials in source code or chat.
- Do not complete official encrypted `echostr` decryption until an official `WXBizMsgCrypt` compatible library is available.
- Do not send real outbound requests to `qyapi.weixin.qq.com` in this round.
- Do not add real sticker or voice media upload.
- Do not deploy public HTTPS in this round.

## Credential Inputs

The local service reads these environment variables:

| Variable | Meaning |
|---|---|
| `WECOM_CORP_ID` | Enterprise CorpID |
| `WECOM_KF_SECRET` | WeChat Customer Service secret used for access token and message sending |
| `WECOM_KF_TOKEN` | Callback token used for signature verification |
| `WECOM_KF_ENCODING_AES_KEY` | Callback AES key |
| `WECOM_OPEN_KFID` | Customer service account ID used when sending messages |
| `WECOM_CALLBACK_PUBLIC_URL` | Public HTTPS callback URL to paste into the WeCom admin console |

## Acceptance Criteria

- Missing configuration returns a clear checklist and never prints secret values.
- Signature verification passes when the signature is generated from sorted `token`, `timestamp`, `nonce`, and encrypted payload.
- Callback GET returns a clear `crypto_not_configured` response when signature is valid but AES decryption is unavailable.
- Plaintext/dev POST events can still be normalized and routed through the existing companion flow.
- Text outbound payloads contain `touser`, `open_kfid`, `msgtype: text`, and `text.content`.
- The admin UI shows live credential route readiness separately from the local mock.

## References

- Enterprise WeChat message receiving requires URL, Token, and EncodingAESKey and verifies callbacks through GET.
- Enterprise WeChat callback signatures use token, timestamp, nonce, and encrypted message content.
- WeChat Customer Service send-message payloads include `touser`, `open_kfid`, `msgtype`, and a message body such as `text.content`.
