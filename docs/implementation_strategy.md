# Implementation Strategy

## Recommended Strategy

Build the MVP as a modular monolith with a background worker and one database.

This means the first product is one coherent backend, but its internal parts are separated cleanly: WeChat adapter, message inbox, safety, memory, AI orchestration, multimodal decision, media assets, distillation, admin, and observability.

## Decision Table

| Option | What It Means In Product Terms | Strengths | Tradeoffs | Fit |
|---|---|---|---|---|
| A. Modular monolith + worker | One backend app, one database, clear internal modules, background jobs for message processing | Fastest stable MVP, easy to debug, enough structure for safety and admin | Later scaling may require splitting modules | Recommended |
| B. Serverless functions | Many small cloud functions handle webhooks, AI calls, media, admin | Low idle cost, simple deployment for small traffic | Harder local debugging, async flow can become scattered | Good if hosting cost is the top priority |
| C. Microservices from day one | Separate services for WeChat, AI, memory, media, admin | Scales cleanly later | Too much overhead for owner + few friends | Not recommended for MVP |

## Recommended Build Order

1. Backend foundation and database.
2. Admin console shell based on the confirmed prototype.
3. User whitelist and memory controls.
4. Conversation simulator for local testing without WeChat.
5. Safety Guard.
6. Personality Engine and Conversation Orchestrator.
7. Multimodal Decision Layer for text, sticker intent, and short voice scripts.
8. Public sample source status and behavior-rule ingestion.
9. WeChat Channel Adapter.
10. Media Asset Layer for approved sticker and voice routes.
11. Observability, error states, and user-level test scripts.

## MVP Technology Shape

The exact framework can be decided in the master task board, but the implementation should preserve these product boundaries:

- Backend: one app with API routes, webhook route, and worker.
- Database: stores users, settings, limited memory, source status, message metadata, and audit events.
- Admin frontend: uses the confirmed static prototype as the screen reference.
- AI provider adapter: swappable so model choice can change later.
- Media provider adapter: swappable so sticker and voice routes can change later.

## WeChat Route

The first implementation should keep WeChat as an adapter, not the center of the whole product. Product logic should work in a local simulator first, then connect to WeChat.

This protects the project from platform friction:

- We can test personality, safety, memory, and multimodal decisions before API credentials are ready.
- If WeChat media rules force stickers to be sent as images, only the adapter/media layer changes.
- If the customer-service route has session limits, the adapter can expose those limits to the response planner.

## What Will Not Be Built First

- Public registration.
- Payment.
- Personal WeChat automation.
- Real-person voice cloning.
- Full sticker asset download.
- Full model fine-tuning.
- Large-scale multi-user analytics.

## Architecture Acceptance Criteria

The architecture is ready for task-board generation when:

- The owner accepts the modular monolith MVP route.
- WeChat, media, memory, safety, AI, admin, and distillation boundaries are clear.
- Major product risks are visible.
- The next stage can split work into small, testable build steps.

