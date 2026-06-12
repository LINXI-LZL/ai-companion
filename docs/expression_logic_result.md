# Expression Logic Result

## Decision

| Field | Value |
|---|---|
| Result date | 2026-06-13 |
| Status | Pass |
| Related smoke test | `docs/expression_logic_smoke_test.md` |

## Accepted Scope

| Area | Result |
|---|---|
| Poetic or ambiguous message | Pass |
| AI quality feedback | Pass |
| Work-rant personality shape | Pass |
| Dify expression guardrail | Pass |
| Short ping / interjection | Pass |
| Repeated generic message | Pass |
| Template-analysis wording filter | Pass |

## Evidence

The local reply planner handles poetic or ambiguous messages without unrelated repeated-theme suffixes, handles `我觉得你不太智能` as direct AI feedback, and keeps work-rant replies in the accepted `刀子嘴豆腐心` shape.

During Dify-mode smoke testing, Dify drifted on poetic and feedback messages. The router now rejects external replies that omit the required expression shape and falls back to the local accepted reply.

The latest screenshot issue came from generic fallback wording that sounded like chat-log analysis, such as `你又提到`, `第三次出现`, `按字面接住`, and `不强行升华`. Those phrases were removed from local reply templates, short pings like `嗳嗳嗳` and `能听见我说话不` now use a dedicated friend-like `short_ping` scenario, and external provider replies containing that template-analysis style are rejected before sending.

Full suite after this repair: 87 tests passed.

## Owner Note

Restart the `8765` service once after this repair so the formal local app loads the new Dify expression guardrail.
