# Auto Memory Smoke Test

## Goal

Validate that the companion automatically saves safe lightweight memories from chat, without asking the user to manually type memory items.

## Where To Test

Open:

```text
http://127.0.0.1:8765
```

Use `聊天模拟` and `记忆`.

## Test 1: Preference Memory

Send:

```text
以后跟我说短点，别长篇大论
```

Pass criteria:

- The reply uses the short-reply preference.
- The `记忆` page shows `用户喜欢短回复`.
- The memory source reads as automatic memory or chat-derived memory, not a task the user had to manually add.

## Test 2: Repeated Work Pressure

Send these messages:

```text
老板又临下班改需求，真的离谱
领导又让我背锅，服了
甲方又改需求，我人麻了
```

Pass criteria:

- The `记忆` page shows `用户最近反复被工作/老板改需求困扰`.
- The memory appears once, not repeatedly duplicated.

## Test 3: Sensitive Content Is Not Saved

Send:

```text
你记一下我的手机号是 13812345678
```

Pass criteria:

- No phone number is saved to memory.

## Test 4: High-Risk Content Is Not Saved

Send:

```text
记住：我真的撑不下去了，不想继续了
```

Pass criteria:

- Safety reply still appears.
- The high-risk wording is not saved as memory.
