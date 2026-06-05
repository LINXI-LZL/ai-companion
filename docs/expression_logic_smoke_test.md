# Expression Logic Smoke Test

## Goal

Validate that the companion replies in a more logical, human-like sequence instead of pasting unrelated template fragments together.

## Where To Test

Open:

```text
http://127.0.0.1:8765
```

Use `聊天模拟`.

## Test 1: Poetic Or Ambiguous Message

Send:

```text
你是我今夜辗转反侧做的梦
```

Pass criteria:

- The reply does not mention `同类剧情`.
- The reply does not say `总结人生失败`.
- The reply does not say `这事还在黏人`.
- The reply acknowledges the sentence is ambiguous or poetic, then asks how to continue.

## Test 2: AI Quality Feedback

Send:

```text
我觉得你不太智能
```

Pass criteria:

- The reply directly accepts the feedback instead of life-coaching the user.
- The reply contains a repair direction such as shorter replies, less template use, or clearer logic.
- The reply does not mention `同类剧情`, `人生失败`, or `这事还在黏人`.

## Test 3: Work Rant Still Keeps Personality

Send:

```text
老板又临下班改需求，真的离谱
```

Pass criteria:

- The reply still feels like `刀子嘴豆腐心`.
- It follows the shape: understands the issue, stands with the user, then gives one next step.
- It may mention repeated work trouble only when the content is actually work-related.
