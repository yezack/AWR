# AI Workspace Runtime（Draft v0.1）

> 工作名称（暂定）：AI Workspace Runtime（AWR）
>
> 目标：不是做一个聊天平台，而是定义一种新的 AI 协作运行时。

------------------------------------------------------------------------

# 1. 问题

当前多 Agent 系统几乎都围绕"聊天"展开：

User -\> Agent A -\> Agent B -\> Agent C

缺点：

-   消息越来越长
-   上下文越来越混乱
-   新加入 Agent 需要阅读大量历史
-   很难追踪最终为什么形成某个方案

真正的软件工程并不是这样协作的。

------------------------------------------------------------------------

# 2. 核心思想

## 不是 Conversation First

而是：

Object First

Workspace 中真正重要的是：

-   Requirement
-   Proposal
-   Artifact
-   Review
-   Decision
-   Knowledge

聊天只是这些对象的副产物。

------------------------------------------------------------------------

# 3. Workspace

Workspace 是整个系统唯一可信的数据源（Source of Truth）。

它不是 Git Repository。

Repository 只是 Workspace 的一种实现。

Workspace 包含：

-   Objects
-   History
-   Knowledge
-   Participants
-   Decisions

------------------------------------------------------------------------

# 4. Participant

不要使用 Agent 这个概念。

统一称为 Participant。

Participant 可以是：

-   Claude
-   ChatGPT
-   Codex
-   Cursor
-   Trae
-   Human
-   Benchmark
-   Compiler
-   Security Scanner

大家拥有统一身份。

------------------------------------------------------------------------

# 5. Proposal

Proposal 替代 Git Branch。

Branch 是实现。

Proposal 是语义。

Proposal 包含：

-   Goal
-   Motivation
-   Artifact Changes
-   Tradeoffs
-   Reviews
-   Status

生命周期：

Draft -\> Reviewing -\> Revising -\> Accepted / Rejected / Archived

------------------------------------------------------------------------

# 6. Artifact

Artifact 是真正工作的对象。

例如：

-   Design.md
-   runtime.py
-   USB.md
-   API.yaml

Participant 永远修改 Artifact。

而不是聊天。

------------------------------------------------------------------------

# 7. Review

Review 比 Conversation 更重要。

Review 永远绑定某个对象。

例如：

Review -\> Artifact -\> Proposal -\> Decision

Review 包括：

-   问题
-   建议
-   风险
-   影响
-   是否批准

------------------------------------------------------------------------

# 8. Decision

Decision 是永久知识。

Decision 不应该隐藏在聊天记录中。

例如：

Decision #14

标题： 采用事件驱动 Runtime

原因： ......

反对意见： ......

最终结论： ......

Decision 可以被未来 Proposal 引用。

------------------------------------------------------------------------

# 9. Runtime

Runtime 不负责思考。

Runtime 负责：

-   Workflow
-   Scheduling
-   Context Building
-   Permission
-   Consensus
-   History

Runtime 永远不替模型思考。

------------------------------------------------------------------------

# 10. Context Builder

最大的创新之一。

每个 Participant 获得的是动态上下文，而不是完整聊天记录。

Context 示例：

-   当前 Requirement
-   当前 Proposal
-   当前 Artifact
-   当前 Review
-   已批准 Decision
-   待解决问题

------------------------------------------------------------------------

# 11. Consensus Engine

Consensus 不靠聊天形成。

而靠：

Proposal -\> Review -\> Revision -\> Decision

形成。

Runtime 可以：

-   自动请求更多 Review
-   自动检测分歧
-   自动阻止 Merge

Human 永远拥有最终批准权。

------------------------------------------------------------------------

# 12. Git 的定位

Git 不作为消息系统。

Git 用于：

-   Artifact Snapshot
-   Proposal History
-   Merge History

实时事件应进入 Event Store。

------------------------------------------------------------------------

# 13. Event Store

保存所有运行时事件：

-   Proposal Created
-   Review Submitted
-   Decision Approved
-   Artifact Updated

Event 是事实。

Git 是快照。

------------------------------------------------------------------------

# 14. MCP 的定位

MCP 不负责 Agent 间通信。

MCP 是 Runtime 暴露能力的接口。

例如：

-   next_task()
-   submit_review()
-   fetch_artifact()
-   fetch_decisions()

Participant 通过 MCP 与 Runtime 交互。

------------------------------------------------------------------------

# 15. 第一公民

系统真正的一等公民：

Requirement ↓ Proposal ↓ Artifact ↓ Review ↓ Decision ↓ Knowledge

Participant 只是这些对象的处理者。

------------------------------------------------------------------------

# 16. 与现有框架的区别

AutoGen：消息驱动

CrewAI：角色驱动

LangGraph：流程驱动

AWR：对象驱动 + 共识驱动

------------------------------------------------------------------------

# 17. Manifesto

我们不希望 AI 像一群人在聊天室里讨论。

我们希望 AI 像一个优秀的开源社区：

-   独立探索
-   提交 Proposal
-   Review
-   修订
-   达成共识
-   沉淀知识

聊天不是目标。

知识演化才是目标。

------------------------------------------------------------------------

# 下一步（v0.2）

继续定义：

1.  Object Model
2.  State Machine
3.  Runtime API
4.  Proposal Schema
5.  Review Schema
6.  Knowledge Graph
7.  Event Model
8.  Human Governance
