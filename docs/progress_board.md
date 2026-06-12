# Progress Board

## Current Position

| Field | Content |
|---|---|
| Current phase | Build Round 4 WeCom real callback and text send |
| Current step | Owner real callback and text-send smoke test |
| Overall status | ready_for_owner_test |
| Completed substeps | 77 / 78 |
| User action needed | Set real WeCom env vars and run the public callback plus text-send smoke test |
| Next step after confirmation | If real text receive/send passes, choose real stickers, voice provider, cursor persistence, or broader agent quality |

## Completed Outputs

| Phase | Completed | Main Outputs |
|---|---:|---|
| Intake | 2 / 2 | `docs/product_intake.md` |
| Product blueprint | 8 / 8 | `docs/product_blueprint.md`, design spec, public source plan, behavior rules |
| Static prototype | 4 / 4 | `web_prototype/index.html`, `docs/screen_specs.md`, `docs/ui_preview.md` |
| Architecture | 3 / 3 | `docs/architecture_overview.md`, `docs/module_boundary.md`, `docs/implementation_strategy.md` |
| Master task board | 2 / 2 | `docs/master_task_board.md`, `docs/progress_board.md`, `docs/artifact_registry.md` |
| Build round scoping | 1 / 1 | `docs/build_scope_current_round.md` |
| Development | 14 / 14 | `app/`, `tests/`, `README.md`, local app at `http://127.0.0.1:8765` |
| User testing | 2 / 2 | `docs/test_intervention_notice.md`, `docs/smoke_test_result.md` |
| UAT docs | 2 / 2 | `docs/uat_scripts.md`, `docs/acceptance_checklist.md` |
| Debug collaboration | 2 / 2 | `docs/bug_feedback_template.md`, `docs/debug_next_actions.md` |
| Delivery | 2 / 2 | `docs/delivery_summary.md`, `docs/handoff_notes.md` |
| Build Round 2 personality quality | 4 / 4 | personality design spec, implementation plan, scenario-aware reply engine, smoke test script, acceptance result |
| Build Round 3 WeCom live credential route | 5 / 5 | live route design spec, implementation plan, `wecom_live` adapter, server endpoints, admin self-check, acceptance result |
| Auto lightweight memory polish | 4 / 4 | automatic memory design spec, implementation plan, auto memory extractor, server wiring, automatic memory UI, acceptance result |
| Expression logic polish | 4 / 4 | regression tests, meta-feedback scenario, generic reply cleanup, Dify expression guardrail, acceptance result |
| External multi-model router | 7 / 7 | selected route C, provider router design spec, implementation plan, router core, server integration, admin status UI, regression tests, acceptance result |
| GitHub open-source radar | 1 / 1 | `docs/github_open_source_radar.md` |
| Dify provider integration | 7 / 7 | Dify design spec, owner design confirmation, implementation plan, provider source, automated tests, status/README docs, app prompt template, acceptance result |
| Build Round 4 WeCom real callback | 3 / 4 | real callback design spec, implementation plan, AES callback crypto, encrypted POST receive, quick ACK queue, callback/message dedupe, sync_msg body pull, send_msg text send, smoke test doc, result note |

## Ready For Test

| Flow | Where | Status |
|---|---|---|
| Local app | `http://127.0.0.1:8765` | running |
| Automated tests | `tests/` | 90 passing |
| Owner smoke test | `docs/smoke_test_result.md` | passed after one wording fix |
| WeChat entry mock | `WeChat Entry` tab | ready for local simulation |
| UAT scripts | `docs/uat_scripts.md` | ready to use |
| Acceptance checklist | `docs/acceptance_checklist.md` | accepted |
| Delivery summary | `docs/delivery_summary.md` | ready |
| Handoff notes | `docs/handoff_notes.md` | done |
| Personality smoke test | `docs/personality_round_2_smoke_test.md` | passed |
| Personality result | `docs/personality_round_2_result.md` | accepted |
| WeCom live route smoke test | `docs/wecom_live_round_3_smoke_test.md` | ready for owner test |
| WeCom live route result | `docs/wecom_live_round_3_result.md` | passed |
| Automatic memory smoke test | `docs/auto_memory_smoke_test.md` | passed |
| Automatic memory result | `docs/auto_memory_result.md` | accepted |
| Expression logic smoke test | `docs/expression_logic_smoke_test.md` | ready for owner test |
| Expression logic result | `docs/expression_logic_result.md` | passed |
| Multi-model router smoke test | `docs/multi_model_router_smoke_test.md` | ready for owner test |
| Multi-model router result | `docs/multi_model_router_result.md` | passed |
| Dify provider smoke test | `docs/dify_provider_smoke_test.md`, `docs/dify_app_prompt_template.md`, `docs/dify_provider_result.md` | passed |
| Memory chain repair | `docs/memory_chain_repair_result.md` | accepted |
| WeCom real callback and text send smoke test | `docs/wecom_real_callback_smoke_test.md` | ready for owner test |
| WeCom real callback and text send result | `docs/wecom_real_callback_result.md` | ready for owner smoke test |

## Waiting For Owner Smoke Test

WeCom real callback and text-send smoke test is pending because it requires real Enterprise WeChat settings plus a public HTTPS callback URL.

## Not Started Yet

| Phase | Remaining Work |
|---|---|
| sync_msg cursor persistence | Persist and continue multi-page customer-service message pulls |
| Real media assets | Sticker and voice upload/provider tracks remain deferred |

## Current Blocker

No local engineering blocker is active for text callback receive/send. Real Enterprise WeChat verification still requires a public HTTPS URL reachable by the platform; sticker assets, voice assets, and cursor persistence remain deferred.
