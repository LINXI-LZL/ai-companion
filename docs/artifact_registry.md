# Artifact Registry

| Artifact ID | Artifact | Type | Location | Related phase | Related step | Summary |
|---|---|---|---|---|---|---|
| artifact-001 | Product intake | document | `docs/product_intake.md` | phase-01-intake | step-01-02-intake | Project starting point, maturity, and risks |
| artifact-002 | Meeting notes | document | `docs/meeting_notes.md` | phase-02-blueprint | step-02-05-blueprint | Structured idea intake notes |
| artifact-003 | Product blueprint | document | `docs/product_blueprint.md` | phase-02-blueprint | step-02-05-blueprint | Confirmed product scope |
| artifact-004 | Decision log | document | `docs/decision_log.md` | phase-02-blueprint | step-02-05-blueprint | Product and technical decisions |
| artifact-005 | Design spec | design_spec | `docs/superpowers/specs/2026-06-04-wechat-ai-companion-design.md` | phase-02-blueprint | step-02-06-design-spec | Confirmed design specification |
| artifact-006 | Project state | other | `docs/project_state.json` | phase-02-blueprint | step-02-06-design-spec | Machine-readable project state |
| artifact-007 | Public data source manifest | other | `data/public_sources/data_sources.json` | phase-02-blueprint | step-02-07-public-sources | Public sample source and license manifest |
| artifact-008 | Public sample distillation plan | document | `docs/public_sample_distillation_plan.md` | phase-02-blueprint | step-02-07-public-sources | Public-source distillation approach |
| artifact-009 | Public sample schema | document | `docs/public_sample_schema.md` | phase-02-blueprint | step-02-07-public-sources | Unified sample format |
| artifact-010 | Behavior distillation rules | document | `docs/behavior_distillation_rules.md` | phase-02-blueprint | step-02-08-multimodal-realism | Deep-night friend behavior rules |
| artifact-011 | Synthetic seed behavior examples | other | `samples/public/seed_behavior_examples.jsonl` | phase-02-blueprint | step-02-08-multimodal-realism | Project-owned seed examples |
| artifact-012 | Screen specs | document | `docs/screen_specs.md` | phase-03-static-prototype | step-03-02-screen-map | Prototype page list and review criteria |
| artifact-013 | UI preview note | document | `docs/ui_preview.md` | phase-03-static-prototype | step-03-02-screen-map | Static prototype review instructions |
| artifact-014 | Web static prototype | web_prototype | `web_prototype/index.html` | phase-03-static-prototype | step-03-03-static-prototype | Clickable static prototype |
| artifact-015 | Architecture overview | architecture_doc | `docs/architecture_overview.md` | phase-04-architecture | step-04-01-architecture-overview | High-level system architecture |
| artifact-016 | Module boundary | architecture_doc | `docs/module_boundary.md` | phase-04-architecture | step-04-02-module-boundaries | Module responsibilities and test boundaries |
| artifact-017 | Implementation strategy | architecture_doc | `docs/implementation_strategy.md` | phase-04-architecture | step-04-03-implementation-strategy | MVP architecture route and build order |
| artifact-018 | Master task board | task_board | `docs/master_task_board.md` | phase-05-master-task-board | step-05-01-master-board | Full phase and substep task board |
| artifact-019 | Progress board | task_board | `docs/progress_board.md` | phase-05-master-task-board | step-05-01-master-board | Current status summary |
| artifact-020 | Artifact registry | task_board | `docs/artifact_registry.md` | phase-05-master-task-board | step-05-01-master-board | Traceable artifact index |
| artifact-021 | Build Round 1 scope | document | `docs/build_scope_current_round.md` | phase-06-build-round-scoping | step-06-01-build-scope-round-1 | Scope for the local companion simulator and admin foundation |
| artifact-022 | Build Round 1 implementation plan | implementation_plan | `docs/superpowers/plans/2026-06-05-build-round-1-local-companion.md` | phase-07-development | step-07-01-project-scaffold | Implementation plan for the local companion simulator |
| artifact-023 | Local companion app source | source_code | `app/` | phase-07-development | step-07-14-mvp-integration | Python, SQLite, and static frontend source for the local app |
| artifact-024 | Automated tests | test | `tests/` | phase-07-development | step-07-14-mvp-integration | Unit and smoke tests for core behavior, storage, API, and static app wiring |
| artifact-025 | Test intervention notice | document | `docs/test_intervention_notice.md` | phase-08-user-test-guidance | step-08-01-test-notice | Owner testing guide for Build Round 1 |
| artifact-026 | Local run instructions | document | `README.md` | phase-07-development | step-07-01-project-scaffold | Local run and test commands |
| artifact-027 | WeChat adapter prototype | source_code | `app/wechat_adapter.py` | phase-07-development | step-07-12-wechat-adapter | Local-only inbound normalizer and outbound envelope for future WeChat integration |
| artifact-028 | UAT scripts | document | `docs/uat_scripts.md` | phase-09-uat-docs | step-09-01-uat-scripts | Nontechnical test scripts for local owner and inner-test validation |
| artifact-029 | Acceptance checklist | document | `docs/acceptance_checklist.md` | phase-09-uat-docs | step-09-02-acceptance-checklist | Build Round 1 pass/fail criteria and deferred items |
| artifact-030 | Bug feedback template | document | `docs/bug_feedback_template.md` | phase-10-debug-collaboration | step-10-01-bug-template | Structured issue report format for chat, page, adapter, and safety problems |
| artifact-031 | Owner smoke test result | document | `docs/smoke_test_result.md` | phase-08-user-test-guidance | step-08-02-owner-smoke-test | Smoke-test evidence, resolved display issue, and next decision |
| artifact-032 | Debug next actions | document | `docs/debug_next_actions.md` | phase-10-debug-collaboration | step-10-02-debug-next-actions | No active repair queue and issue ledger after Build Round 1 acceptance |
| artifact-033 | Delivery summary | document | `docs/delivery_summary.md` | phase-11-delivery | step-11-01-delivery-summary | Build Round 1 delivered source, docs, flows, deferred items, and verification |
| artifact-034 | Handoff notes | document | `docs/handoff_notes.md` | phase-11-delivery | step-11-02-handoff-notes | How to run, verify, maintain boundaries, and choose Build Round 2 focus |
| artifact-035 | Build Round 2 personality design | design_spec | `docs/superpowers/specs/2026-06-05-personality-quality-round-2-design.md` | phase-12-personality-quality | step-12-02-spec-plan | Confirmed `刀子嘴豆腐心` behavior rules and acceptance criteria |
| artifact-036 | Build Round 2 implementation plan | implementation_plan | `docs/superpowers/plans/2026-06-05-personality-quality-round-2.md` | phase-12-personality-quality | step-12-02-spec-plan | Test-first implementation plan for scenario-aware personality quality |
| artifact-037 | Personality smoke test | document | `docs/personality_round_2_smoke_test.md` | phase-12-personality-quality | step-12-04-owner-smoke-test | Owner test script for work rants, self-blame, safety override, and light companion scenes |
| artifact-038 | Scenario-aware reply engine | source_code | `app/orchestrator.py` | phase-12-personality-quality | step-12-03-personality-engine | Reply planner with scenario metadata, scenario turn counts, and `刀子嘴豆腐心` reply packs |
| artifact-039 | Personality quality tests | test | `tests/test_companion_core.py`, `tests/test_storage_api.py` | phase-12-personality-quality | step-12-03-personality-engine | Automated checks for variation, self-blame boundaries, safety override, and work-rant three-beat replies |
| artifact-040 | Build Round 2 acceptance result | document | `docs/personality_round_2_result.md` | phase-12-personality-quality | step-12-04-owner-smoke-test | Owner accepted the `刀子嘴豆腐心` personality upgrade |
