# Personality Quality Round 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the local companion so the selected `刀子嘴豆腐心` personality varies naturally across repeated themes while keeping safety boundaries.

**Architecture:** Keep the existing modular monolith. Add scenario detection and scenario turn counting inside `app/orchestrator.py`, because reply planning already lives there and the change does not need new storage tables.

**Tech Stack:** Python standard library, SQLite-backed message history, `unittest`, vanilla static frontend.

---

## File Structure

- Modify `tests/test_companion_core.py` for direct reply-planning behavior.
- Modify `tests/test_storage_api.py` for history-backed variation behavior.
- Modify `app/orchestrator.py` for scenario classification, turn counts, and `刀子嘴豆腐心` reply packs.
- Update project docs after implementation: `docs/master_task_board.md`, `docs/progress_board.md`, `docs/artifact_registry.md`, `docs/project_state.json`, and `docs/acceptance_checklist.md`.

## Tasks

### Task 1: Lock The Personality Contract With Tests

**Files:**
- Modify: `tests/test_companion_core.py`
- Modify: `tests/test_storage_api.py`

- [ ] **Step 1: Add failing tests**

Add tests for self-blame boundaries, high-risk serious mode, and ten similar work-rant turns.

- [ ] **Step 2: Run targeted tests**

Run:

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_companion_core tests.test_storage_api -v
```

Expected before implementation: at least one new test fails because scenario metadata and ten-turn variation are not implemented.

### Task 2: Implement Scenario-Aware Reply Planning

**Files:**
- Modify: `app/orchestrator.py`

- [ ] **Step 1: Add scenario detection**

Classify the message into a small scenario id such as `work_boss`, `procrastination`, `self_blame`, `missing`, `boredom`, `night_emo`, `relationship`, `greeting`, `identity`, or `generic`.

- [ ] **Step 2: Count recent scenario turns**

Use existing `recent_messages` and their `incoming_text` values. Do not add a new database table.

- [ ] **Step 3: Generate replies from scenario packs**

Return varied replies that follow the three-beat pattern: feeling, playful jab, small next step or question.

- [ ] **Step 4: Preserve safety and media behavior**

Keep high-risk safety replies first. Keep existing `mode`, `sticker_intent`, `voice_intent`, and `voice_script` contracts.

### Task 3: Verify And Update Project State

**Files:**
- Modify: `docs/master_task_board.md`
- Modify: `docs/progress_board.md`
- Modify: `docs/artifact_registry.md`
- Modify: `docs/project_state.json`
- Modify: `docs/acceptance_checklist.md`

- [ ] **Step 1: Run full tests**

Run:

```powershell
& 'C:\Users\25968\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```

Expected after implementation: all tests pass.

- [ ] **Step 2: Update docs**

Record Build Round 2 as personality quality, style `刀子嘴豆腐心`, and status ready for owner test.

- [ ] **Step 3: Commit**

Commit the spec, plan, tests, implementation, and state updates together after verification.
