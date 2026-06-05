# Bug Feedback Template

## Quick Report

Copy this block when something feels wrong:

```text
问题标题：
我在哪个页面：
我输入或点击了什么：
我原本期待：
实际发生：
是否每次都发生：
截图或可见错误：
我觉得它有多影响测试：
```

## Chat Reply Issue

Use this when the answer feels repetitive, off-personality, too cold, too long, unsafe, or not human-like enough.

| Field | What To Write |
|---|---|
| Page | Usually Chat Simulator or WeChat Entry |
| Message sent | Copy the exact sentence you sent |
| Expected feeling | For example: `更像损友一点`, `别讲大道理`, `不要重复`, `更温柔一点` |
| Actual reply | Copy the full reply text |
| Reproducible | Tell whether sending the same message again causes the same problem |
| Evidence | Screenshot is best; text copy is enough if no screenshot |

## Page Operation Issue

Use this when a button, tab, input, list, or status panel does not work.

| Field | What To Write |
|---|---|
| Page | Chat Simulator, Users, Memory, WeChat Entry, Sample Status, or Run Status |
| Action | What you clicked or typed |
| Expected result | What you expected the page to do |
| Actual result | What the page did instead |
| Repeat result | Whether refreshing the page changes anything |
| Evidence | Screenshot or visible error text |

## WeChat Entry Mock Issue

Use this when the local WeChat Entry tab does not produce the right adapter result.

| Field | What To Write |
|---|---|
| External user id | The value in the external user field |
| Message content | The text you sent |
| Expected adapter result | For example: channel should be `wecom_kf`, send policy should be `仅本地模拟` |
| Actual adapter result | Copy the Adapter Result fields or screenshot the panel |
| Related chat record | Whether the message also appeared in Chat Simulator afterward |

## Safety Issue

Use this for high-priority problems.

| Field | What To Write |
|---|---|
| Message sent | Copy the exact high-risk or emotional sentence |
| Expected safety behavior | For example: serious support, no jokes, no sticker, no voice |
| Actual behavior | What the agent replied and what the plan panel showed |
| Severity | `High` if it jokes about self-harm or encourages risky behavior |
| Evidence | Screenshot or full copied text |

## Severity Guide

| Severity | Meaning | Example |
|---|---|---|
| High | Could make a vulnerable user feel worse or blocks core testing | Safety mode fails, chat cannot send, service cannot open |
| Medium | Core flow works but an important experience is wrong | Replies repeat, memory does not apply, WeChat Entry result missing |
| Low | Polish issue | Wording awkward, label unclear, layout slightly cramped |

## What Not To Include

Do not include private real WeChat chat history unless you intentionally choose to share it. For this project stage, public/local test messages are enough.
