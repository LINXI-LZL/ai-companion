# Build Round 3 WeCom Live Route Smoke Test

## Goal

Validate that the project now has a real Enterprise WeChat / WeChat Customer Service credential-route skeleton while keeping secrets out of source code and chat.

## Where To Test

Open:

```text
http://127.0.0.1:8765
```

Use the `微信入口` tab.

## Test 1: Live Self-Check Panel

Look for `真实接入自检`.

Pass criteria:

- The panel shows `企业微信客服真实通道`.
- If no environment variables are set, it should show missing configuration instead of crashing.
- Secret values must not be printed anywhere.
- `回调解密` should say that the official crypto library is missing until `WXBizMsgCrypt` support is added.

## Test 2: Status API

Open:

```text
http://127.0.0.1:8765/api/wecom-live/status
```

Pass criteria:

- Response contains `channel: wecom_live`.
- Response contains `missing_fields` when credentials are absent.
- Response says `send_mode: payload_only`.
- Response does not reveal any real secret value.

## Test 3: Existing Local Mock Still Works

In `微信入口`, use the existing `模拟微信入站` form.

Pass criteria:

- Local mock still produces an outbound text envelope.
- The companion personality still uses the accepted `刀子嘴豆腐心` style.

## Test 4: Real Callback Boundary

This round does not complete real Enterprise WeChat URL verification yet. It can validate the callback request signature shape, but real `echostr` decryption still needs the official `WXBizMsgCrypt` compatible library.

Pass criteria:

- The product clearly says this is not ready for real encrypted callback verification yet.
- No one needs to paste real CorpID, Secret, Token, or EncodingAESKey into chat.

## Next Required User-Side Setup

When ready for real WeCom testing, prepare these values outside chat:

- `WECOM_CORP_ID`
- `WECOM_KF_SECRET`
- `WECOM_KF_TOKEN`
- `WECOM_KF_ENCODING_AES_KEY`
- `WECOM_OPEN_KFID`
- `WECOM_CALLBACK_PUBLIC_URL`

The callback URL must be a public URL reachable by Enterprise WeChat, usually HTTPS.
