# Multi-Model Router Result

## Decision

| Field | Value |
|---|---|
| Result date | 2026-06-13 |
| Status | Pass |
| Related smoke test | `docs/multi_model_router_smoke_test.md` |

## Accepted Scope

| Area | Result |
|---|---|
| Default local fallback | Pass |
| Dify configured mode | Pass |
| Secret redaction | Pass |
| Chat continuity | Pass |
| Safety local-first behavior | Pass |
| Required memory fallback | Pass |
| Required expression fallback | Pass |

## Evidence

The router status reports active provider and configured models without exposing API keys. Local mode reports `router_disabled`, while the current configured service reports Dify as active and configured.

Safety messages stay local-first with `fallback_reason: safety_mode`. Required memory and required expression-shape guardrails fall back to the local accepted reply when the external model omits critical context.
