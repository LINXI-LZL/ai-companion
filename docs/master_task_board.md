# Master Task Board

## Control Summary

| Field | Content |
|---|---|
| Project | 微信树洞 AI |
| Current phase | User test guidance |
| Current step | Owner smoke test |
| Overall status | Ready for owner test |
| Total phases | 11 |
| Total substeps | 42 |
| Completed substeps | 37 |
| Needs user attention | Yes |
| Next action | Run the owner smoke test and review the acceptance checklist |
| Current risk | Real credentialed WeChat integration, real sticker assets, and real voice synthesis remain deferred after local flow validation |

## Full Board

| Phase ID | Step ID | Phase | Substep | Goal | Output | Dependency | Status | User action | Needs confirmation | Testable after step | Blockers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| phase-01-intake | step-01-01-context | Intake | Explore project context | Confirm project starting point | Workspace check | none | done | none | no | no | none |
| phase-01-intake | step-01-02-intake | Intake | Create intake artifact | Establish project start state | `docs/product_intake.md` | step-01-01-context | done | none | no | no | none |
| phase-02-blueprint | step-02-01-personality | Product blueprint | Choose AI personality | Define agent feeling | B + D 深夜损友 | phase-01-intake | done | none | no | no | none |
| phase-02-blueprint | step-02-02-scenario | Product blueprint | Choose MVP scenario | Avoid first-version sprawl | 生活压力/emo/睡前陪伴 | step-02-01-personality | done | none | no | no | none |
| phase-02-blueprint | step-02-03-user-scope | Product blueprint | Choose user scope | Define inner-test size | 你 + 少数朋友 | step-02-02-scenario | done | none | no | no | none |
| phase-02-blueprint | step-02-04-wechat-route | Product blueprint | Choose WeChat route | Balance experience and platform risk | 企业微信/微信客服式入口 | step-02-03-user-scope | done | none | no | no | none |
| phase-02-blueprint | step-02-05-blueprint | Product blueprint | Consolidate blueprint | Produce confirmed product scope | `docs/product_blueprint.md` | step-02-04-wechat-route | done | none | no | no | none |
| phase-02-blueprint | step-02-06-design-spec | Product blueprint | Write design spec | Save confirmed design | `docs/superpowers/specs/2026-06-04-wechat-ai-companion-design.md` | step-02-05-blueprint | done | none | no | no | none |
| phase-02-blueprint | step-02-07-public-sources | Product blueprint | Confirm public sources | Avoid private chat burden | `data/public_sources/data_sources.json` | step-02-06-design-spec | done | none | no | no | none |
| phase-02-blueprint | step-02-08-multimodal-realism | Product blueprint | Define multimodal realism | Add sticker and voice behavior scope | `docs/behavior_distillation_rules.md` | step-02-07-public-sources | done | none | no | no | none |
| phase-03-static-prototype | step-03-01-prototype-review-mode | Static prototype | Confirm prototype mode | Move to visual confirmation | User requested prototype | step-02-08-multimodal-realism | done | none | no | no | none |
| phase-03-static-prototype | step-03-02-screen-map | Static prototype | Create screen specs | Define pages and flow | `docs/screen_specs.md` | step-03-01-prototype-review-mode | done | none | no | no | none |
| phase-03-static-prototype | step-03-03-static-prototype | Static prototype | Build prototype | Let user inspect UI | `web_prototype/index.html` | step-03-02-screen-map | done | none | no | yes | none |
| phase-03-static-prototype | step-03-04-ui-confirmation | Static prototype | Confirm prototype | Gate before coding | User confirmed in browser | step-03-03-static-prototype | done | none | no | yes | none |
| phase-04-architecture | step-04-01-architecture-overview | Architecture | Create overview | Explain system structure | `docs/architecture_overview.md` | step-03-04-ui-confirmation | done | none | no | no | none |
| phase-04-architecture | step-04-02-module-boundaries | Architecture | Define module boundaries | Prevent tangled build | `docs/module_boundary.md` | step-04-01-architecture-overview | done | none | no | no | none |
| phase-04-architecture | step-04-03-implementation-strategy | Architecture | Choose strategy | Pick MVP build route | `docs/implementation_strategy.md` | step-04-02-module-boundaries | done | none | no | no | none |
| phase-05-master-task-board | step-05-01-master-board | Master task board | Generate master task board | Split project into trackable steps | `docs/master_task_board.md` | step-04-03-implementation-strategy | done | none | no | no | none |
| phase-05-master-task-board | step-05-02-board-confirmation | Master task board | Confirm master task board | Gate before implementation tracking | User confirmed master board | step-05-01-master-board | done | none | no | no | none |
| phase-06-build-round-scoping | step-06-01-build-scope-round-1 | Build round scoping | Scope build round 1 | Define first implementation slice | `docs/build_scope_current_round.md` | step-05-02-board-confirmation | done | none | no | no | none |
| phase-07-development | step-07-01-project-scaffold | Development | Project scaffold | Create runnable app foundation | `app/`, `README.md` | step-06-01-build-scope-round-1 | done | none | no | yes | none |
| phase-07-development | step-07-02-database-schema | Development | Database schema | Store users, settings, memory, logs | SQLite schema in `app/storage.py` | step-07-01-project-scaffold | done | none | no | yes | none |
| phase-07-development | step-07-03-admin-shell | Development | Admin console shell | Match confirmed prototype structure | `app/static/index.html` | step-07-01-project-scaffold | done | none | no | yes | none |
| phase-07-development | step-07-04-users-whitelist | Development | Users and whitelist | Control inner-test access | User API and UI | step-07-02-database-schema | done | none | no | yes | none |
| phase-07-development | step-07-05-conversation-simulator | Development | Conversation simulator | Test without WeChat credentials | Local chat simulator | step-07-03-admin-shell | done | none | no | yes | none |
| phase-07-development | step-07-06-safety-guard | Development | Safety Guard | Stop unsafe playful replies | `app/safety.py` and tests | step-07-05-conversation-simulator | done | none | no | yes | none |
| phase-07-development | step-07-07-memory-service | Development | Memory Service | Store limited preference memory | Memory API and controls | step-07-04-users-whitelist | done | none | no | yes | none |
| phase-07-development | step-07-08-orchestrator | Development | Orchestrator and personality | Generate deep-night friend response plan | `app/orchestrator.py` | step-07-06-safety-guard | done | none | no | yes | none |
| phase-07-development | step-07-09-multimodal-decision | Development | Multimodal decision layer | Choose text, sticker, voice, or safety | `app/multimodal.py` | step-07-08-orchestrator | done | none | no | yes | none |
| phase-07-development | step-07-10-distillation-status | Development | Distillation source status | Expose public source readiness | Source status UI/API | step-07-03-admin-shell | done | none | no | yes | none |
| phase-07-development | step-07-11-media-layer | Development | Media asset layer stub | Defer real assets while supporting intent | `app/media.py` and media asset fallback | step-07-09-multimodal-decision | done | none | no | yes | none |
| phase-07-development | step-07-12-wechat-adapter | Development | WeChat adapter prototype | Isolate platform receive/send logic | `app/wechat_adapter.py`, `/api/wechat/mock-inbound`, `WeChat Entry` tab | step-07-11-media-layer | done | none | no | yes | Real credentialed WeChat API mapping remains future work |
| phase-07-development | step-07-13-observability | Development | Observability and audit | Make failures visible | Status API, server log, audit events | step-07-12-wechat-adapter | done | none | no | yes | none |
| phase-07-development | step-07-14-mvp-integration | Development | End-to-end MVP integration | Connect core flow | Runnable local MVP | step-07-13-observability | done | run_user_test | yes | yes | none |
| phase-08-user-test-guidance | step-08-01-test-notice | User test guidance | Prepare test notice | Tell user what to test now | `docs/test_intervention_notice.md` | step-07-14-mvp-integration | done | none | no | no | none |
| phase-08-user-test-guidance | step-08-02-owner-smoke-test | User test guidance | Owner smoke test | Verify core flows with owner | Smoke test result | step-08-01-test-notice | ready_for_test | run_user_test | yes | yes | User must test |
| phase-09-uat-docs | step-09-01-uat-scripts | UAT docs | Write UAT scripts | Give nontechnical test steps | `docs/uat_scripts.md` | step-08-01-test-notice | done | none | no | no | none |
| phase-09-uat-docs | step-09-02-acceptance-checklist | UAT docs | Acceptance checklist | Define pass/fail criteria | `docs/acceptance_checklist.md` | step-09-01-uat-scripts | waiting_user | review_output | yes | no | Needs owner review |
| phase-10-debug-collaboration | step-10-01-bug-template | Debug collaboration | Bug feedback template | Make user reports actionable | `docs/bug_feedback_template.md` | step-09-01-uat-scripts | done | none | no | no | none |
| phase-10-debug-collaboration | step-10-02-debug-next-actions | Debug collaboration | Debug next actions | Turn issues into fixes | `docs/debug_next_actions.md` | step-10-01-bug-template | not_started | provide_bug_feedback | yes | no | Waits for issues |
| phase-11-delivery | step-11-01-delivery-summary | Delivery | Delivery summary | Summarize delivered work | `docs/delivery_summary.md` | step-10-02-debug-next-actions | not_started | none | no | no | none |
| phase-11-delivery | step-11-02-handoff-notes | Delivery | Handoff notes | Prepare next-iteration handoff | `docs/handoff_notes.md` | step-11-01-delivery-summary | not_started | review_output | yes | no | none |

## Current Confirmation Gate

Open `http://127.0.0.1:8765` and run the owner smoke test from `docs/test_intervention_notice.md`, including the new `WeChat Entry` tab. Then review `docs/acceptance_checklist.md`.
