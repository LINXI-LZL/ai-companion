# WeCom Real Callback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable real Enterprise WeChat callback URL verification and encrypted text callback receive handling.

**Architecture:** Extend the existing `app/wecom_live.py` adapter instead of replacing the local mock path. Keep outbound delivery as `payload_only`, and route decrypted text callbacks through the existing companion chat engine.

**Tech Stack:** Python standard library HTTP server, pure-Python AES-256-CBC, XML parsing with `xml.etree.ElementTree`, existing storage and companion modules.

---

### Task 1: Callback Crypto

**Files:**
- Modify: `tests/test_wechat_adapter.py`
- Modify: `app/wecom_live.py`

- [x] **Step 1: Write failing crypto tests**

Add coverage for AES-256-CBC known-vector encryption/decryption and encrypted `echostr` validation.

- [x] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_wechat_adapter -v
```

Expected before implementation: import errors for AES and encryption helpers.

- [x] **Step 3: Implement minimal crypto support**

Add EncodingAESKey decoding, WeCom packet padding, AES-256-CBC encrypt/decrypt, CorpID validation, and URL verification decryption.

- [x] **Step 4: Verify task tests**

Run the same command and confirm the crypto tests pass.

### Task 2: Encrypted POST Callback

**Files:**
- Modify: `tests/test_wechat_adapter.py`
- Modify: `app/wecom_live.py`
- Modify: `app/server.py`

- [x] **Step 1: Write failing encrypted callback test**

Add a test that encrypts a text XML callback, verifies the signature, routes the message through the companion engine, and expects `ack_text: success`.

- [x] **Step 2: Implement callback receive path**

Add encrypted XML extraction, decrypt/parse/normalize logic, `create_wecom_live_callback_response`, and POST `/api/wecom-live/callback`.

- [x] **Step 3: Preserve outbound boundary**

Return `success` to Enterprise WeChat and keep generated reply as a local `outbound_payload`.

### Task 3: Owner-Facing Readiness

**Files:**
- Modify: `app/static/app.js`
- Modify: `README.md`
- Create: `docs/wecom_real_callback_smoke_test.md`
- Create: `docs/wecom_real_callback_result.md`

- [x] **Step 1: Update readiness labels**

Show `ready`, `key_ready`, `missing_encoding_aes_key`, and `invalid_encoding_aes_key` without exposing secrets.

- [x] **Step 2: Add owner smoke test**

Document environment variables, callback URL, expected status API response, and common failure meanings.

- [x] **Step 3: Update README**

Document the callback endpoint and make clear that real outbound sending is still deferred.

### Task 4: Verification

**Files:**
- Modify: project tracking docs

- [x] **Step 1: Run full tests**

Run:

```powershell
python -m pytest
```

Result: 76 tests passed.

- [x] **Step 2: Validate project state JSON**

Run:

```powershell
python -m json.tool docs\project_state.json > $null
```

Result: exit code 0.
