# GitHub 开源项目雷达

## 文档目标

这份雷达用来判断哪些 GitHub 开源项目值得我们学习、试接或规避。它不是下载清单，也不是直接换技术栈的建议。核心目标是：在不破坏当前微信树洞 AI 产品边界的前提下，从成熟项目里吸收微信/企微接入、多模型主脑、长期记忆、语音、表情包和后台配置经验。

复核日期：2026-06-12

## 雷达分层

| 分层 | 含义 |
|---|---|
| 立即借鉴概念 | 现在就可以参考它的架构思想，但不盲目复制代码 |
| 后续试接 | 值得在当前烟测通过后做一次小范围技术验证 |
| 持续观察 | 有参考价值，但暂时不适合进入产品实现 |
| 不建议直接使用 | 对当前产品有明显合规、许可证、成本或产品边界风险 |

## 总体建议

继续保留我们当前的小而稳的本地产品核心，不要直接迁移到大型开源平台。开源项目应作为参考层：

1. 优先研究 `LangBot` 和 `CowAgent` 的通道、模型、记忆、后台配置设计。
2. 后续把 `Dify` 做成外部主脑 provider，而不是让它替换整个系统。
3. `Wechaty` 和个人微信自动化只作为研究参考，不作为正式路线。
4. 语音和表情包单独开路线，先做许可证和素材权利检查。

## 项目雷达表

| 项目 | 分层 | 对我们最有用的点 | 适配度 | 主要风险 |
|---|---|---|---|---|
| [LangBot](https://github.com/langbot-app/LangBot) | 立即借鉴概念 | 生产级 IM 机器人架构、WeChat/WeCom 通道、插件系统、多模型接入、后台管理 | 很高 | 平台体量大，不适合直接替换我们的 MVP |
| [CowAgent](https://github.com/zhayujie/CowAgent) | 立即借鉴概念 | 微信式 AI 助手、多通道、长期记忆、技能/工具、多模态能力 | 很高 | 范围很大，直接采用会把产品拉成通用 Agent 平台 |
| [Dify](https://github.com/langgenius/dify) | 后续试接 | 外部工作流、RAG、Agent、提示词调试、运行日志、模型管理 | 高 | 许可证有附加条件，自部署会增加运维成本 |
| [dify-on-wechat](https://github.com/hanfangyuan4396/dify-on-wechat) | 后续试接 | 微信入口转发到 Dify 的胶水层 | 中 | 下游分支，需要检查活跃度和接口稳定性 |
| [Wechaty](https://github.com/wechaty/wechaty) | 持续观察 | 个人微信机器人抽象、消息事件、测试 mock | 中 | 个人微信自动化存在封号和合规风险 |
| [ChatTTS](https://github.com/2noise/ChatTTS) | 持续观察 | 朋友式短语音、笑声、停顿、口语韵律 | 中 | AGPL 代码和非商业模型条款，产品化前必须法务/许可证复核 |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | 后续试接 | 少样本声音克隆和自定义 TTS 流程 | 中 | 声音克隆必须有明确授权和滥用控制 |
| [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) | 持续观察 | 用户发语音后的 ASR、情绪识别、音频事件检测 | 中 | 模型和运行依赖较重，文字优先 MVP 暂时不需要 |
| [fish-speech](https://github.com/fishaudio/fish-speech) | 持续观察 | 高质量开源 TTS 研究 | 中 | 研究许可证，商业/产品使用需要谨慎复核 |
| [Int-RA / StickerInt](https://github.com/HITSZ-HLT/Int-RA) | 持续观察 | 表情包检索、意图识别、贴纸回复选择思路 | 低 | 仓库仍提示 code will be released soon，数据集和素材权利也要检查 |

## 重点项目判断

### LangBot

LangBot 是当前最值得拆架构的参考项目。它对我们的价值主要在：

- 一个机器人核心服务多个 IM 平台
- 浏览器后台配置模型、通道和运行状态
- 插件系统和事件驱动结构
- 访问控制、限流、敏感词、监控和异常处理
- 对 Dify、Coze、n8n、Langflow、DeepSeek、Gemini、OpenAI 兼容模型、本地模型等的集成经验

我们应该这样用它：

- 保留当前 `app/server.py` 和 `app/llm_router.py`。
- 借鉴“平台适配器 + 插件事件 + 后台配置”的结构。
- 不把当前 MVP 迁移成 LangBot，除非我们决定转型为通用机器人平台。

### CowAgent

CowAgent 和用户最初想象的“微信好友式 AI”很接近：多通道、Web 控制台、长期记忆、技能、工具、语音、文件和多模型。它最值得参考的是“AI 伴随用户成长”的设计。

我们应该这样用它：

- 研究它的长期记忆层级和周期性蒸馏思路。
- 研究它的模型/通道配置后台。
- 借鉴“技能/工具”的概念，但不要把我们的树洞 AI 做成泛任务助理。

### Dify

Dify 不应该替代我们的产品逻辑。它更适合作为一个外部主脑 provider：

```text
微信/企微入口
  -> 本地安全判断 + 轻量记忆 + 表情/语音意图
  -> llm_router
      -> OpenAI / DeepSeek / Gemini
      -> Dify workflow API
      -> 本地兜底
```

这样我们仍然掌握安全边界、记忆策略、多模态意图和微信入口，同时可以让 Dify 负责复杂提示词、RAG、流程编排和运行日志。

### Wechaty

Wechaty 值得用来研究消息对象、事件命名、bot mock 和历史微信机器人实现。但它不适合作为我们当前正式路线，因为我们已经选择更稳的企业微信/微信客服式入口。

适合参考：

- 消息事件设计
- 本地 mock
- bot 生命周期

不建议用于：

- 直接控制个人微信号作为生产入口

### 语音项目

语音路线要独立推进。用户想要“像真人一样发语音”，但不等于第一步就做声音克隆。

推荐顺序：

1. 继续保留短语音脚本。
2. 先接一个托管 TTS provider 或 Dify TTS 节点。
3. 再评估 GPT-SoVITS、ChatTTS、fish-speech。
4. 只有在明确授权、算力、许可证、滥用控制都准备好后，才尝试定制音色。
5. 如果用户以后会发语音，再评估 SenseVoice 做语音识别和情绪识别。

### 表情包项目

表情包可以先学行为逻辑，不急着复用素材。

当前建议：

- 继续使用 `sticker_intent`。
- 后续建立“用户授权/自制/可商用”的小表情包素材库。
- 研究 StickerInt/StickerConv 类项目时，只学习“什么时候发什么表情”的逻辑，不直接复制图片。

## 推荐接入路线

| 顺序 | 工作 | 原因 | 用户影响 |
|---:|---|---|---|
| 1 | 完成当前多模型路由烟测 | 先确认本地/外部主脑切换稳定 | 用户验证当前页面 |
| 2 | 给 `app/llm_router.py` 增加 `dify` provider | 能把部分对话交给 Dify workflow/RAG | 需要 Dify app key |
| 3 | 参考 LangBot/CowAgent 做通道适配器审计 | 让企微/微信入口更稳 | 用户无需操作 |
| 4 | 参考 CowAgent 设计长期记忆蒸馏 | 从简单自动记忆升级到更像真人的长期记忆 | 用户审核记忆行为 |
| 5 | 做语音 provider 选择 | 在托管 TTS 和本地开源 TTS 之间取舍 | 用户选择成本/隐私/质量 |
| 6 | 做表情包素材权利路线 | 避免素材侵权和体验割裂 | 用户批准素材来源 |

## 与当前代码的对应关系

| 当前模块 | 可参考项目 | 可能升级点 |
|---|---|---|
| `app/llm_router.py` | Dify、LangBot、CowAgent | 增加 Dify、Coze、Ollama、OpenAI-compatible gateway 等 provider |
| `app/wecom_live.py` | LangBot、CowAgent | 抽象更清晰的平台适配器和消息信封 |
| `app/auto_memory.py` | CowAgent | 记忆分层、周期蒸馏、长期偏好摘要 |
| `app/static/` 后台 | LangBot、CowAgent、Dify | 模型配置页、通道配置页、运行日志页 |
| `app/multimodal.py` | ChatTTS、GPT-SoVITS、StickerInt | 表情/语音意图到真实素材的映射 |

## 许可证与安全备注

- 优先借鉴 Apache-2.0 和 MIT 项目的结构。
- Dify 是基于 Apache 2.0 并带附加条件的许可证，商业化前要复核。
- ChatTTS、fish-speech、各种模型权重和数据集要单独看 license，不能只看代码仓库。
- 不克隆未经授权的真人声音。
- 不使用未经授权的真实表情包图片。
- 个人微信自动化保持研究用途，除非用户明确接受账号风险。

## 当前推荐结论

不要替换当前应用。我们现在的应用小、清楚、可控，更适合继续迭代。

下一步最实用的是增加 Dify provider：

```text
COMPANION_LLM_PROVIDER=dify
DIFY_API_KEY=...
DIFY_APP_ID=...
```

这样可以拿到 Dify 的 workflow、RAG、Agent 和日志能力，同时继续保留我们自己的安全、记忆、多模态和微信入口边界。
