# Auto Lightweight Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the companion automatically save safe lightweight memories from chat.

**Architecture:** Add a small pure `app/auto_memory.py` extractor and call it from `create_chat_response` before reply planning. Keep storage schema unchanged and avoid duplicate memories by checking existing enabled memory content.

**Tech Stack:** Python standard library, SQLite, vanilla static frontend, `unittest`.

---

## File Structure

- Create `app/auto_memory.py`: rule-based safe memory extraction.
- Modify `app/server.py`: save explicit memory and automatic memory through a dedupe helper before planning.
- Modify `app/static/index.html` and `app/static/app.js`: make the Memory page read as automatic memory management.
- Modify `tests/test_storage_api.py`: cover automatic preference memory, repeated work theme memory, duplicate prevention, sensitive suppression, and high-risk suppression.
- Modify `tests/test_static_app.py`: cover automatic memory page copy.

## Tasks

### Task 1: Add Failing Tests

- [ ] Add storage/API tests for automatic memory extraction and privacy boundaries.
- [ ] Add static UI tests for automatic memory copy.
- [ ] Run targeted tests and confirm failures because `app.auto_memory` and the UI copy do not exist.

### Task 2: Implement Extractor

- [ ] Create `app/auto_memory.py`.
- [ ] Implement sensitive-content and high-risk suppression.
- [ ] Implement preference and repeated-theme rules.

### Task 3: Integrate Chat Flow

- [ ] Update `create_chat_response` to save automatic memories once per user.
- [ ] Keep explicit `记住：` memory behavior.
- [ ] Return updated memory list as before.

### Task 4: Update UI And Project State

- [ ] Update Memory page copy so the user is not asked to manually add memory.
- [ ] Update acceptance checklist, task board, progress board, artifact registry, and project state.

### Task 5: Verify And Commit

- [ ] Run full tests.
- [ ] Run `git diff --check`.
- [ ] Restart local service and smoke-test a chat message that auto-saves memory.
- [ ] Commit the feature.
