# WeCom Live Credential Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a real WeCom credential-route skeleton that can be locally verified without exposing real secrets.

**Architecture:** Keep the local mock adapter intact and create a new `app/wecom_live.py` module for live configuration, signature checks, callback preflight, live event normalization, and text-send payload construction. Add thin HTTP endpoints in `app/server.py` and a small self-check panel in the existing WeChat Entry view.

**Tech Stack:** Python standard library, SQLite-backed local app, vanilla HTML/CSS/JS, `unittest`.

---

## File Structure

- Create `app/wecom_live.py`: environment config, redacted status, SHA1 signature validation, callback preflight, dev/plaintext event normalization, text outbound payloads.
- Modify `app/server.py`: add `/api/wecom-live/status`, `/api/wecom-live/callback`, and `/api/wecom-live/dev-inbound`.
- Modify `app/static/index.html`: add live credential self-check panel under the WeChat Entry tab.
- Modify `app/static/app.js`: fetch and render live status and callback information.
- Modify `tests/test_wechat_adapter.py`: add adapter and API coverage.
- Modify `tests/test_static_app.py`: assert the live self-check UI and API wiring exist.
- Update project tracking docs after code passes.

## Tasks

### Task 1: Adapter Contract Tests

- [ ] Add tests for config redaction, missing-field status, signature generation/verification, callback preflight without crypto support, dev event normalization, and text send payload shape.
- [ ] Run `tests.test_wechat_adapter` and confirm the new tests fail because `app.wecom_live` does not exist.

### Task 2: Adapter Implementation

- [ ] Create `app/wecom_live.py` with small pure functions and no real network calls.
- [ ] Run `tests.test_wechat_adapter` and confirm adapter tests pass.

### Task 3: Server Endpoint Tests

- [ ] Add tests for `/api/wecom-live/status`, `/api/wecom-live/callback`, and `/api/wecom-live/dev-inbound`.
- [ ] Run targeted tests and confirm failures before server implementation.
- [ ] Implement the endpoints in `app/server.py`.
- [ ] Run targeted tests and confirm they pass.

### Task 4: Admin Self-Check UI

- [ ] Add self-check markup to the WeChat Entry tab.
- [ ] Add frontend rendering for config readiness, public callback URL, missing fields, and live-channel state.
- [ ] Update static tests to detect the new UI and API route wiring.

### Task 5: Project State And Verification

- [ ] Update `docs/master_task_board.md`, `docs/progress_board.md`, `docs/artifact_registry.md`, `docs/project_state.json`, and `docs/acceptance_checklist.md`.
- [ ] Run full tests: `python -m unittest discover -s tests -v`.
- [ ] Run `git diff --check`.
- [ ] Restart the local service if needed and verify `/api/wecom-live/status`.
- [ ] Commit the full third-round implementation.
