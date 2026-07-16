# AWR RFC-0001 — The Conversation Trap (Draft v0.1)

> **Status:** Reviewing（已收 HY3 评审，本修订吸收评审结论）
> **Version:** v0.1（自 v0.0 修订）
> **Reviewers:** HY3
> **Based on:** [HY3-Review-RFC-0001.md](../NOTES/HY3-Review-RFC-0001.md)
> **Supersedes:** RFC-0001 v0.0
>
> **Purpose**
>
> 本文不是项目介绍，不是 README，也不是技术实现文档。
>
> 它是一份思想文档（RFC），用于在不同 AI 之间传递 AWR
> 的核心理念，并邀请其他 AI 对理论进行审查、反驳和完善。

------------------------------------------------------------------------

## 变更记录（v0.0 → v0.1）

| 变更 | 说明 |
|------|------|
| Axiom #1 弱化 | 从全称定律改为有作用域的设计原则 |
| 新增 Thread 对象 | 对话不被消灭，而是被定型为有界可溯源的一等对象 |
| 新增 Claim / Divergence | 比 Decision 更基础的抽象；承载未决冲突 |
| 新增 Goal / Problem | 比 Requirement 更前置的对象 |
| 区分 Artifact / Record | Knowledge Object 下分可变与不可变两类 |
| 修正 Workspace 表述 | "saves Reality" → "保存显式状态（对象图）" |
| 引用既有理论 | IBIS、ADR、Blackboard Architecture |
| 移除评审请求 | 已收评审；改为总结评审结论 |
| 添加元数据头 | Status / Version / Reviewers |

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

> **AWR 不认为 Conversation 应该成为 AI 协作系统的存储模型。**

但——

> **对话不应被消灭。对话应被提升为有界、可溯源的一等对象（Thread）。**

------------------------------------------------------------------------

# 一个思想实验（修订后）

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

> **修订注（HY3）：** Linux 思想实验是预设结论的——它同时拿走了对象层和对话。公平对照应是「对象+对话」vs「仅对象」。本 RFC 承认这个批评。我们不是要证明「仅对象」更好；我们要证明的是「对象为主体 + 对话被定型」优于「对话为主体 + 对象被淹没」。Axiom #1 已从全称定律弱化为有作用域的设计原则（见下文）。

------------------------------------------------------------------------

# AWR 的假设（修订后）

AWR 提出以下设计原则：

> 对复杂、持久、多参与者的协作，持久对象图作为状态模型，比消息日志更具可扩展性。

对称地：

> 对话仍负责对象的*生成*与*意义对齐*，不应被消灭，而应被*定型*——每条对话归属于一个 Thread 对象，Thread 是生成 Knowledge Object 的容器。

如果该原则成立，那么：

Conversation 不应成为 Runtime 的核心存储模型，但应成为一等对象（Thread）。

------------------------------------------------------------------------

# AWR 设计原则（Design Principles）

## DP-1：Object First, Conversation Typed

系统不以 Agent 为中心，也不以 Conversation 为中心。

而是以 **Knowledge Object** 为中心。

对话被提升为 **Thread**——有界、可溯源的一等对象。

Thread 包含：goal、participants、以及 `derived_from` / `produces` 指针指向产出的对象。

## DP-2：Object Graph as State

Workspace 保存项目共享的**显式状态**（对象图），而非 Reality 本身。

## DP-3：Runtime Doesn't Think

Runtime 只负责：Workflow、Scheduling、Persistence、Permission、Governance。

思考、推理、判断委托给 Participant。

## DP-4：Human Governance

Human 永远保留最终治理权。

### 设计原则之间的关系

```
DP-1 (Object First, Conversation Typed)
  ├── 定义"什么是一等公民"：Knowledge Object + Thread
  ├── 对话不被消灭，而是被定型
  └── 指引：新抽象进来时，问"它是 Knowledge Object 还是 Thread？"
DP-2 (Object Graph as State)
  ├── 定义"状态存什么"：显式对象图
  └── 指引：Workspace ≠ Reality；隐性知识缺口被显式承认
DP-3 (Runtime Doesn't Think)
  ├── 定义"Runtime 边界"：调度≠判断
  └── 指引：分歧检测委托给 Reviewer Participant
DP-4 (Human Governance)
  ├── 定义"谁说了算"：Human 最终裁决
  └── 指引：自动共识的范围由 Human 预先划定
```

------------------------------------------------------------------------

# 第一公民：Knowledge Object

Knowledge Object 分为两大类：

## Artifact（可变、带版本）

-   Requirement
-   Proposal
-   Design
-   Code
-   Document

Artifact 可以修改、有版本历史、存储在 Git（内容寻址 @sha）。

## Record（不可变事件/决定）

-   Review
-   Decision
-   Thread（对话记录）

Record 一旦创建不可修改；存储在 Event Store（append-only）。

### 对象层次

比现有对象更基础的抽象（HY3 建议补充）：

```
Goal / Problem              ← 新增：比 Requirement 更前置
    ↓
Requirement                 ← 已有
    ↓
Proposal                    ← 已有
    ↓
Artifact（Design/Code/...） ← 已有
    ↓
Review                      ← 已有
    ↓
Claim                       ← 新增：比 Decision 更基础
    ├── status: hypothesis / contested / accepted / rejected
    └── Decision = Claim(status=accepted)
    ↓
Divergence / OpenQuestion   ← 新增：承载未决冲突、不兼容 Decision
```

未来可能扩展：

-   Benchmark
-   Experiment
-   Failure
-   Proof

> 这些不作为 Core，仅标为「可能的实验产出」。遵循 Problem Driven Evolution——先在真实项目证明必要性再加 Core。

------------------------------------------------------------------------

# Thread（对话定型）

**Thread 是对话被提升为一等对象后的形态。**

| 属性 | 说明 |
|------|------|
| goal | Thread 的目标 |
| participants | 参与该对话的 Participant |
| messages | 对话记录（不可变） |
| produces | 该 Thread 产出的 Knowledge Object（可多个） |
| status | open / resolved / archived |

Thread 解决了一个根本矛盾：

- "我们需要对话来生成对象"
- "对象才是第一公民"

这两个陈述不再矛盾——因为每个对象都有 `derived_from: Thread`。对话不再是被淹没的存储模型，而是被定型、被溯源的有界对象。

------------------------------------------------------------------------

# Workspace

Workspace 不是聊天窗口。

Workspace 保存项目共享的**显式状态**（对象图）。

它回答：

-   当前有哪些 Goal / Problem？
-   当前有哪些 Proposal 正在 Review？
-   哪些 Decision 已经成为共识？
-   哪些 Divergence 尚未解决？

Workspace 保存显式状态，而非 Reality。

------------------------------------------------------------------------

# Participant

AWR 使用 Participant，而不是 Agent。

Participant 只是 Knowledge 的生产者与消费者。

系统中心始终是 Workspace。

## 能力类别（HY3 建议）

Participant 不应扁平对待。按能力类别分层：

| 类别 | 示例 | 权限特征 | 共识权重 |
|------|------|----------|----------|
| 推理型 | Claude, ChatGPT, Gemini | 可提交 Proposal/Review | 按领域权重 |
| 工具型 | Compiler, Linter | 只读 + 自动检查 | 否决权（reject only） |
| 治理型 | Human | 最终审批 | 最高 |
| 自动检查型 | Security Scanner, Benchmark | 只读 + 自动检查 | 否决权（reject only） |

> 具体权重规则留待 RFC-000X（Governance）定义。

------------------------------------------------------------------------

# Runtime

Runtime 不负责：

-   思考
-   推理
-   判断谁正确
-   检测分歧（委托给 Reviewer Participant）

Runtime 只负责：

-   Workflow
-   Scheduling
-   Persistence
-   Permission
-   Governance
-   状态机（推动 Proposal 生命周期）

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

**机器速度的治理**是 AWR 真正的新问题（HY3）：当 Participant 一小时产 100 个 Proposal，人类终审成瓶颈，自动共识可能失控。Human Governance 需要分层——哪些 Decision 可自动共识、哪些必须人类审批。留待 RFC-000X（Governance）展开。

------------------------------------------------------------------------

# 既有理论基础（必须正视）

AWR 的单个构件都不新；新意在于**综合** + 「异构 AI Participant 即开源贡献者」隐喻 + 治理立场。

| 理论 | 年份 | 与 AWR 的关系 |
|------|------|---------------|
| **IBIS** (Issue-Based Information System, Kunz & Rittel) | 1970 | Issue→Position→Argument 建模设计审议；AWR 的 Review/Decision 是弱类型 IBIS |
| **Blackboard Architecture** (Corkill) | 1980s | Agent 写共享黑板而非互相发消息——AWR 本质是类型化黑板系统 |
| **Linda Tuple Space** (Gelernter) | 1980s | 共享状态协作 |
| **ADR** (Architecture Decision Records, Nygard) | 2011 | Decision ≈ ADR，「决策即永久知识」就是 ADR 思想 |
| **SECI 模型** (Nonaka & Takeuchi) | 1995 | 隐性↔显性知识转化；暴露 AWR 的隐性知识缺口 |
| **CSCW / Articulation Work** (Strauss) | 1980s | artifact/review/decision 承载协作是 CSCW 核心 |

AWR 的贡献是**为异构 AI 参与者设计的框架与治理模型**，不是对象本体论。

------------------------------------------------------------------------

# 当前未解决的问题

AWR 故意没有回答：

-   Git 是否适合作为 Artifact 内容存储的底层？
-   Proposal 是否替代 Branch？
-   Review 是否应该具有权重？权重如何计算？
-   Participant 能力类别的具体定义与权限模型
-   共识状态机的具体规则（法定人数、超时、死锁处理）
-   成本 / 延迟 / 可观测性模型

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

# 评审结论（HY3，已吸收）

1.  **Axiom #1 作为全称公理会被推翻；作为有作用域的设计原则立得住。** → 已修正。
2.  **对话不应被消灭，而应被定型为有界对象。** → 新增 Thread 对象。
3.  **需要补充 Claim、Divergence、Goal/Problem 等更基础的抽象。** → 已新增。
4.  **必须引用 IBIS、ADR、Blackboard 等既有理论。** → 已引用。
5.  **"Workspace saves Reality" 最危险。** → 已修正为"保存显式状态（对象图）"。
6.  **Knowledge Object 应分为可变（Artifact）和不可变（Record）。** → 已区分。
7.  **Participant 不应与 Knowledge Object 同级。** → 已按能力类别分层。
8.  **「Chief Architect = RFC corpus 与挑战流程的管家」。** → 已接受。

------------------------------------------------------------------------

# 修订后的 AWR 设计原则

> **DP-1: Object First, Conversation Typed.**
>
> 持久对象图作为状态模型；对话被定型为 Thread。

> **DP-2: Object Graph as State.**
>
> Workspace 保存显式状态（对象图）。

> **DP-3: Runtime Doesn't Think.**
>
> Runtime 只调度与持久化；判断委托给 Participant。

> **DP-4: Human Governance.**
>
> Human 最终裁决；自动共识范围由 Human 预先划定。

------------------------------------------------------------------------

# 仓库结构（建议）

```
AWR/
│
├── RFC/
│   ├── RFC-0001-The-Conversation-Trap.md      ← 本文
│   ├── RFC-0002-Object-Model.md               （待起草）
│   ├── RFC-0003-Governance.md                 （待起草）
│   └── ...
│
├── NOTES/
│   ├── HY3-Review-RFC-0001.md
│   ├── HY3-Review-AWR-Draft-v0.1.md
│   └── ...
│
├── EXPERIMENTS/
│   └── ...
│
├── SPEC/
│   ├── Object-Model.md
│   ├── Event-Model.md
│   └── ...
│
└── IMPLEMENTATION/
    └── ...
```

RFC 是项目最重要的资产，不是代码。因为代码以后一定会重写很多次。但是如果 RFC 足够成熟，它会一直指导实现。

---

> **Chief Architect 的职责 = RFC corpus 与挑战流程的管家，而非正确性的裁决者。**
