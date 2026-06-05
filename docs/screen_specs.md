# Screen Specs

## Prototype Goal

Confirm the user-facing chat flow and lightweight admin console for 微信树洞 AI before formal implementation. The prototype must show how the AI feels like a late-night sharp-tongued friend, how sticker and voice decisions appear, and how public sample distillation feeds the behavior layer.

## Page List

| Page | Purpose | Key Elements | Confirmation Question |
|---|---|---|---|
| Chat Experience | Show the WeChat-like conversation and response decision flow | Conversation thread, quick scenario buttons, response-mode timeline, sticker and voice preview | Does this feel close to a WeChat friend instead of a chatbot dashboard? |
| Multimodal Strategy | Show when the agent uses text, sticker, voice, or safety response | Mode matrix, trigger rules, current decision card, deferred asset warnings | Are the sticker and voice choices understandable and controllable? |
| Users And Memory | Show inner-test user management and memory boundaries | User list, whitelist state, memory cards, tone sliders | Does the memory feel useful without being creepy? |
| Sample Distillation | Show public source status and behavior-rule pipeline | Source tiers, license status, deferred downloads, seed samples | Is it clear which sources are usable now and which wait until VPN is off? |
| Safety And Ops | Show crisis fallback and operating status | Safety mode examples, risk switch, integration readiness, run health | Is the product safety boundary visible enough before development? |

## Primary Flow

1. Admin opens the prototype on Chat Experience.
2. Admin reviews a late-night user message.
3. Agent response shows text, sticker intent, voice intent, and safety state.
4. Admin switches to Multimodal Strategy to inspect why the agent chose that mode.
5. Admin checks Users And Memory to confirm per-user tone and memory controls.
6. Admin checks Sample Distillation to see public source readiness and deferred downloads.
7. Admin checks Safety And Ops to confirm safety fallback is visible before implementation.

## Interaction Requirements

- Navigation tabs must switch the main content without page reload.
- Scenario buttons must update the chat preview and decision panel.
- Tone controls must visually change selected values.
- Source cards must clearly show candidate, research-only, deferred, and method-reference states.
- Safety examples must show playful mode becoming unavailable for high-risk content.

## Prototype Non-Goals

- No real WeChat API connection.
- No real AI model call.
- No real sticker, voice, or dataset download.
- No authentication.
- No production admin permissions.

