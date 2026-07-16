# AWR RFC-0002 — Workspace

> **Status:** Draft
> **Version:** v0.1
> **Author:** AWR corpus (consolidated from RFC-0001 v0.1, SPEC v0.2)
> **Based on:** [RFC-0001 The Conversation Trap](../RFC/0001-conversation-trap.md), [RFC-0004 Knowledge Object](../RFC/0004-knowledge-object.md)
> **Lifecycle:** Draft → Discussion → Accepted → Implemented → Deprecated

> **Purpose**
>
> RFC-0001 把"对话"降级为接口。本文定义那个对话所生产的**共享状态本身**是什么：
> **Workspace = 一个协作项目共享的、显式的对象图（object graph）**，它跨参与者、跨会话、
> 跨实现持久存在。它是 AWR 的"土地"，不是某个 Runtime 的私有内存。

------------------------------------------------------------------------

## 1. 问题陈述

今天的所有协作工具把"workspace"当成**文件夹**或**上下文窗口**：

- 文件夹存字节，但不存"意义"——它不知道哪些文件是 Proposal、哪些是 Decision。
- 上下文窗口是**私有的、易逝的**——每个 AI 只看到自己那一段对话，不看到项目的共享状态。

AWR 拒绝这两点。Workspace 必须是**显式的、可寻址的、跨参与者共享的状态**。

## 2. 核心主张

### 2.1 Workspace = 共享的显式状态（不是文件夹，不是上下文）

```
Workspace := the project's shared explicit state
           = a graph of typed Knowledge Objects (RFC-0004)
           + an append-only event log of how they changed
```

- 每个参与者读写**同一个对象图**，不是各自的私有聊天窗口。
- 这直接落实 Core Belief #5：**Reality should be shared, not context.**

### 2.2 双存储（Dual Storage）

| 存储 | 角色 | 性质 |
|------|------|------|
| **Event Store** | 事实源（source of truth） | append-only、可重放、记录所有状态变更 |
| **Content Store**（Git） | 内容存储 | 内容寻址（Artifact@sha），存可变内容的大块 |

- Event Store 是"日志"；Content Store 是"blob"。
- 两者分离：真相在事件里，内容在 Git 里。一条 Decision 事件用 `@sha` 指向被锁定的 Artifact。
- 这解决了"force-push 让 Decision 悬空"的脆弱性（详见 RFC-0005、PROTOTYPE/EXP-0002）。

### 2.3 Workspace 是可寻址、可查询的

- 每个对象有稳定 ID；参与者**引用**对象而非**复制**它。
- Workspace 不绑定任何 Runtime——它是一个**数据模型 + 协议**，可由多种 Runtime 实现。
- 这正是"Git of AI collaboration"的含义：Workspace 规范活过任何单一 Runtime。

### 2.4 Workspace 独立于 Runtime

Workspace 是一份规范，不是一份实现。今天的 Runtime 明天会被重写；
Workspace 的对象图与事件流应当被任何兼容 Runtime 原样读取。

## 3. 与既有理论的呼应

| 理论 | 本文对应 |
|------|----------|
| **Blackboard** | Workspace ≈ 共享黑板；参与者读写同一块板 |
| **Linda / Tuple Space** | 对象图 ≈ 可被寻址的元组空间 |
| **CSCW** | 共享态是协作系统的一等公民（而非附带产物） |

## 4. 开放问题（邀请挑战）

1. **保留/垃圾**：Event Store 永远 append-only 吗？何时（若 ever）可以 prune？
2. **隐私边界**：什么进共享 Workspace，什么留参与者私有？Human 的思维过程要共享吗？
3. **存储分界**：一个对象的状态变更究竟落在 Event Store 还是 Content Store？边界是否总是清晰？
4. **查询语言**：Workspace 是否需要一种查询/订阅语言（"给我所有 Draft 状态的 Proposal"）？还是这已是 Runtime 关切？
5. **规模**：Event Store 无限增长，重放成本如何控制？

## 5. 当前未决（交给后续 RFC）

- 对象图的具体类型系统 → **RFC-0004（Knowledge Object）**
- 谁有权修改 Workspace、共识如何达成 → **RFC-0005（Governance）**
- Participant 身份与权重 → **RFC-0003（Participant）**

---

> 本文处于 Draft。欢迎以 Reviewer 姿态挑战其隐含假设（尤其"共享显式状态"是否总能成立）。
