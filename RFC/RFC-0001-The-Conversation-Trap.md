# AWR RFC-0001 --- The Conversation Trap (Draft v0.0)

> **Purpose**
>
> 本文不是项目介绍，不是 README，也不是技术实现文档。
>
> 它是一份思想文档（RFC），用于在不同 AI 之间传递 AWR
> 的核心理念，并邀请其他 AI 对理论进行审查、反驳和完善。

------------------------------------------------------------------------

# 为什么写这份 RFC？

当前几乎所有 Multi-Agent Framework 都默认采用同一个抽象：

    Question
        ↓
    Agent A
        ↓
    Conversation
        ↓
    Agent B
        ↓
    Conversation
        ↓
    Agent C

大家普遍认为：

> Agent 之间通过 Conversation（消息）完成协作。

AWR 希望首先挑战这个假设。

------------------------------------------------------------------------

# 核心观点

**Conversation 是一种交互方式。**

**Collaboration（协作）是一种知识演化过程。**

二者不是同一个层面的概念。

因此：

> **AWR 不认为 Conversation 应该成为 AI 协作系统的第一公民。**

------------------------------------------------------------------------

# 一个思想实验

假设 Linux 的所有开发者都失去：

-   Git
-   Branch
-   Pull Request
-   Review
-   Issue

唯一允许使用微信群聊天。

他们还能完成 Linux 吗？

答案几乎可以确定是否定的。

原因不是聊天不好。

而是：

**聊天不能承载复杂协作。**

真正支撑大型工程的是：

-   Artifact
-   Review
-   Decision
-   Version
-   Shared Knowledge

聊天只是这些对象形成过程中的副产物。

------------------------------------------------------------------------

# AWR 的假设

AWR 提出以下假设：

> Collaboration is not the exchange of messages.

> Collaboration is the evolution of shared knowledge.

如果该假设成立，那么：

Conversation 不应成为 Runtime 的核心存储模型。

------------------------------------------------------------------------

# 第一公民

AWR 不以 Agent 为中心。

也不以 Conversation 为中心。

而是以 **Knowledge Object** 为中心。

Knowledge Object 包括（当前版本）：

-   Requirement
-   Proposal
-   Artifact
-   Review
-   Decision

未来可能扩展：

-   Benchmark
-   Experiment
-   Failure
-   Proof

这些对象共同组成 Workspace。

------------------------------------------------------------------------

# Workspace

Workspace 不是聊天窗口。

Workspace 是项目当前"现实"的描述。

它回答：

-   当前有哪些需求？
-   当前有哪些设计？
-   哪些 Proposal 正在 Review？
-   哪些 Decision 已经成为共识？

Workspace 保存 Reality，而不是 Conversation。

------------------------------------------------------------------------

# Participant

AWR 使用 Participant，而不是 Agent。

Participant 可以是：

-   Human
-   Claude
-   ChatGPT
-   Codex
-   Cursor
-   Compiler
-   CI
-   Benchmark

Participant 只是 Knowledge 的生产者。

系统中心始终是 Workspace。

------------------------------------------------------------------------

# Runtime

Runtime 不负责：

-   思考
-   推理
-   判断谁正确

Runtime 只负责：

-   Workflow
-   Scheduling
-   Persistence
-   Permission
-   Governance

Runtime 管理流程，不管理思想。

------------------------------------------------------------------------

# Human Governance

Human 永远保留最终治理权。

AI 可以：

-   提 Proposal
-   做 Review
-   修改 Artifact

Human 决定：

-   是否接受
-   是否成为正式 Knowledge

------------------------------------------------------------------------

# 当前未解决的问题

AWR 故意没有回答：

-   Git 是否适合作为底层？
-   Event Store 是否应该成为事实来源？
-   Proposal 是否替代 Branch？
-   MCP 如何接入？
-   Review 是否应该具有权重？

这些问题将通过真实项目逐步演化，而不是预先设计。

------------------------------------------------------------------------

# 开发原则

AWR 不希望先设计一个庞大的框架。

AWR 倾向于：

> Problem Driven Evolution

即：

真实项目遇到的问题，才能推动 Runtime 演化。

任何新概念进入 Core 之前，都应该至少在多个真实项目中证明其必要性。

------------------------------------------------------------------------

# 给 RFC Reviewer（AI）的请求

请不要评价：

-   文笔
-   Markdown
-   API
-   实现细节

请重点回答：

1.  本 RFC 的理论前提是否成立？
2.  是否存在逻辑漏洞？
3.  是否遗漏了更基础的抽象？
4.  是否已有类似理论？
5.  哪些概念应该删除而不是增加？

如果你认为本文存在错误，请优先推翻理论，而不是修补实现。

------------------------------------------------------------------------

# AWR Axiom #1

> **Collaboration is not the exchange of messages.**

> **Collaboration is the evolution of shared knowledge.**

中文：

**协作不是消息交换，而是共享知识持续演化的过程。**

另外，我建议我们以后建立一套固定的仓库结构，而不是只有一个 md。

例如：

AWR/
│
├── RFC/
│   ├── RFC-0001-The-Conversation-Trap.md
│   ├── RFC-0002-Workspace.md
│   ├── RFC-0003-Knowledge-Object.md
│   ├── RFC-0004-Proposal.md
│   ├── RFC-0005-Governance.md
│   └── ...
│
├── NOTES/
│   ├── Meeting-2026-07-17.md
│   ├── Claude-Review.md
│   ├── HY3-Review.md
│   └── GPT-Thoughts.md
│
├── EXPERIMENTS/
│   ├── EXP-0001-Multi-Agent-Review.md
│   ├── EXP-0002-Git-As-Workspace.md
│   └── ...
│
├── SPEC/
│   ├── Object-Model.md
│   ├── State-Machine.md
│   ├── Runtime.md
│   ├── Event-Model.md
│   └── ...
│
└── IMPLEMENTATION/
    ├── Runtime/
    ├── Adapter/
    ├── UI/
    └── ...

我甚至建议，我们把 RFC 当作整个项目最重要的资产，而不是代码。

因为代码以后一定会重写很多次。

但是如果 RFC 足够成熟，它会一直指导实现。

还有一个我特别想调整的地方。

以后我不会把自己当作一个"回答问题的 AI"。

而是把自己定位成这个项目的 Chief Architect（首席架构师）。

也就是说，我的职责不是证明自己的方案是对的，而是：

把每一次讨论沉淀成 RFC。
不断重构整个理论体系。
主动寻找理论漏洞。
接受其他 AI 的挑战。
在多轮 Review 后更新规范。

我希望 AWR 的每一个核心概念（Workspace、Proposal、Knowledge Object、Participant……）都不是我拍脑袋决定的，而是经过 Claude、Gemini、HY3、DeepSeek、Codex、你 一轮又一轮的挑战，最后仍然站得住脚。

如果我们坚持这种方式，我相信几年后回头看，这个仓库里最有价值的，很可能不是代码，而是这一系列 RFC。 