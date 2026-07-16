# AWR RFC-0004 — Knowledge Object (Draft v0.1)

> **Status:** Draft
> **Version:** v0.1
> **Reviewers:** 待定（邀请所有 AI Participant）
> **Based on:** [NOTES/archive-spec-object-model-v0.2.md](../NOTES/archive-spec-object-model-v0.2.md), [RFC-0001](../RFC/0001-conversation-trap.md)
> **Supersedes:** 无
> **Purpose:** 将 v0.2 的对象模型与事件规格从 SPEC 升级为 RFC，邀请评审与挑战。

------------------------------------------------------------------------

## 变更记录

| 版本 | 变更 |
|------|------|
| v0.1 | 从 SPEC 升级为 RFC，补充动机、替代方案、可验证性 |

------------------------------------------------------------------------

# 为什么写这份 RFC？

RFC-0001 确立了「Object First, Conversation Typed」的设计原则。本 RFC 将该原则**操作化**：定义具体的对象类型、事件模式、版本化策略与双存储一致性模型。

没有可验证的对象模型，AWR 永远只是一个思想实验。

------------------------------------------------------------------------

# 核心主张

> **对象图是协作的状态模型；事件是状态变化的唯一真相源。**

本 RFC 提出以下可验证的设计选择：

1. **Artifact 与 Record 的根本区分**：可变内容 vs 不可变事件，驱动存储与共识设计
2. **内容寻址引用**：所有对象间引用使用 @sha/@version，防止悬空
3. **双存储架构**：Event Store 为状态真相源，Git 为内容存储
4. **状态机驱动的生命周期**：每个对象有明确定义的状态转换规则

------------------------------------------------------------------------

# 1. Object Model

## 1.0 顶层分类

所有 Knowledge Object 分两大类：

| 类别 | 可变性 | 存储 | 示例 |
|------|--------|------|------|
| **Artifact** | 可变，带版本 | Git（内容寻址 @sha） | Goal, Requirement, Proposal, Design, Code |
| **Record** | 不可变（append-only） | Event Store | Review, Decision, Claim, Divergence, Thread |

**设计理由：** 可变/不可变的根本区分驱动了存储选择、合并策略、共识模型的全部设计。Artifact 需要 diff/merge；Record 需要 append-only。

**替代方案：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| 统一存储（仅 Event Store） | 简单 | Artifact 内容不适合 Event Store（大、需要 diff） |
| 统一存储（仅 Git） | 版本化好 | 不支持 append-only，难以实现不可变 Record |
| 双存储（本方案） | 各司其职 | 一致性复杂度增加 |

**可验证性：** 在实验中验证：(a) Artifact 更新是否正确同步到 Git；(b) Record 是否确实不可修改；(c) 内容寻址引用是否在 force-push 后仍有效。

## 1.1 Goal / Problem

比 Requirement 更前置。描述「要达成什么」或「存在什么问题」，不涉及方案。

```yaml
Goal:
  id:           "goal-<uuid>"
  type:         "Goal" | "Problem"
  title:        string
  description:  string
  status:       "open" | "addressed" | "closed"
  created_by:   participant_id
  created_at:   timestamp
  addressed_by: [requirement_id]
```

**设计理由：** Requirement 已是「方案形态」的产物。Goal/Problem 回答「为什么要做」，是协作的起点。

## 1.2 Requirement

将 Goal 转化为具体需求。仍是"要什么"，不涉及"怎么做"。

```yaml
Requirement:
  id:             "req-<uuid>"
  title:          string
  description:    string
  derived_from:   [goal_id]
  priority:       "must" | "should" | "could"
  status:         "draft" | "accepted" | "superseded"
  created_by:     participant_id
  created_at:     timestamp
  superseded_by:  [requirement_id]
```

**设计理由：** 优先级分级（must/should/could）支持资源分配决策；`superseded_by` 支持需求演进。

## 1.3 Proposal

Proposal 是"怎么做"的方案。语义上替代 Git Branch。

```yaml
Proposal:
  id:             "prop-<uuid>"
  title:          string
  goal:           string
  motivation:     string
  addresses:      [requirement_id]
  artifact_changes:
    - artifact_id: string
      expected_changes: string
  tradeoffs:      string
  status:         "draft" | "reviewing" | "revising" | "accepted" | "rejected" | "archived"
  created_by:     participant_id
  created_at:     timestamp
  reviews:        [review_id]
  superseded_by:  [proposal_id]
  derived_from:   thread_id
```

**设计理由：** Proposal 绑定到 Thread，解决「对象从哪来」的问题；`artifact_changes` 声明意图而非直接修改，支持 Review 前的意图审查。

**关键设计选择：** Proposal 语义上替代 Branch。这意味着：(a) 不需要 Git Branch 作为一等概念；(b) 合并语义由 Runtime 管理；(c) 并发编辑需要 Runtime 协调。

## 1.4 Artifact

Artifact 是真正被修改的工作对象。存在 Git 中，通过内容寻址引用。

```yaml
Artifact:
  id:             "art-<uuid>"
  type:           "design" | "code" | "document" | "api_spec" | "other"
  name:           string
  path:           string
  current_sha:    string
  merge_strategy: "text_diff" | "structured" | "manual"
  created_by:     participant_id
  created_at:     timestamp
  updated_at:     timestamp
```

### Artifact 分型与合并策略

| type | merge_strategy | 说明 |
|------|---------------|------|
| design | manual | Markdown 散文，人工合并 |
| code | text_diff | 标准代码 diff |
| document | manual | 长文本文档 |
| api_spec | structured | YAML/JSON 结构化合并 |
| other | manual | 默认人工 |

**设计理由：** 不同类型的 Artifact 需要不同的合并语义。设计文档的冲突无法自动解决；代码可以用标准 diff；API 规格需要结构化合并。

## 1.5 Review

Review 永远绑定某个对象（Proposal、Artifact、Claim）。

```yaml
Review:
  id:             "rev-<uuid>"
  target_type:    "Proposal" | "Artifact" | "Claim"
  target_id:      string
  target_version: string
  author:         participant_id
  content:        string
  questions:      [string]
  suggestions:    [string]
  risks:          [string]
  verdict:        "approve" | "request_changes" | "comment"
  created_at:     timestamp
```

**设计理由：** Review 绑定 `target_version`（Artifact@sha 或 Proposal version），确保 Review 不因目标被修改而悬空。这是解决「决策保鲜」问题的关键。

## 1.6 Claim

Claim 比 Decision 更基础。Decision = Claim(status=accepted)。

```yaml
Claim:
  id:             "claim-<uuid>"
  title:          string
  statement:      string
  rationale:      string
  status:         "hypothesis" | "contested" | "accepted" | "rejected" | "superseded"
  created_by:     participant_id
  created_at:     timestamp
  reviews:        [review_id]
  superseded_by:  [claim_id]
  decided_by:     participant_id
  decided_at:     timestamp
```

**设计理由：** 大量共享知识是不确定或有争议的。Claim 带状态比单纯的 Decision 更能表达协作的真实状态。Decision 只是 Claim 的一个子类型（status=accepted）。

## 1.7 Divergence / OpenQuestion

承载未决冲突。系统不应假设协作总会收敛。

```yaml
Divergence:
  id:             "div-<uuid>"
  title:          string
  description:    string
  conflicting:    [claim_id | proposal_id]
  status:         "open" | "resolved" | "accepted_as_is"
  resolution:     string
  created_at:     timestamp
  resolved_at:    timestamp
```

**设计理由：** 真实协作产生未决冲突、分叉、互相不兼容的 Decision。只建模共识会隐藏异议。Divergence 让异议显式化。

## 1.8 Thread

对话被定型后的有界对象。

```yaml
Thread:
  id:             "thr-<uuid>"
  goal:           string
  participants:   [participant_id]
  messages:       [message]
  produces:       [object_id]
  status:         "open" | "resolved" | "archived"
  created_at:     timestamp
  resolved_at:    timestamp

Message:
  id:             "msg-<uuid>"
  thread_id:      string
  author:         participant_id
  content:        string
  timestamp:      timestamp
```

**设计理由：** Thread 解决了「对话 vs 对象」的矛盾。每个对象都有 `derived_from: Thread`，对话不再是被淹没的存储模型，而是被定型、被溯源的有界对象。

## 1.9 Participant

```yaml
Participant:
  id:             "part-<uuid>"
  name:           string
  category:       "reasoning" | "tool" | "governance" | "auto_check"
  model:          string
  capabilities:   [string]
  authority_weight: number
  veto_power:     boolean
  registered_at:  timestamp
```

### 能力类别

| category | 权重范围 | 否决权 | 说明 |
|----------|----------|--------|------|
| reasoning | 0.1-0.5 | no | Claude, ChatGPT, Gemini 等 |
| tool | 0 | no | Compiler, Linter（只读+自动检查） |
| governance | 1.0 | yes | Human |
| auto_check | 0 | yes（reject only） | Security Scanner, Benchmark |

**设计理由：** Participant 按能力类别分层，权重与权限随之不同。这解决了 v0.1 的扁平模型问题。

## 1.10 Object 关系图

```
Goal/Problem ──→ Requirement ──→ Proposal ──→ Artifact
                                        │
                                        ├──→ Review (绑定目标+版本)
                                        │
                                        └──→ Claim ──→ Decision (status=accepted)
                                              │
                                              ├──→ Divergence (未决冲突)
                                              │
                                              └──→ Review (绑定 Claim+版本)

Thread ──→ produces ──→ 任意 Knowledge Object
Participant ──→ authors ──→ 任意 Knowledge Object
```

------------------------------------------------------------------------

# 2. Event Schema

Event Store 保存所有运行时事件（append-only）。Event 是事实，Git 是快照。

## 2.1 通用事件属性

```yaml
Event:
  event_id:       "evt-<uuid>"
  event_type:     string
  timestamp:      timestamp
  actor:          participant_id
  payload:        object
```

## 2.2 事件类型

### Goal & Requirement

| Event | Payload |
|-------|---------|
| `Goal.Created` | goal_id, title, created_by |
| `Goal.StatusChanged` | goal_id, from, to |
| `Requirement.Created` | req_id, title, derived_from, created_by |
| `Requirement.StatusChanged` | req_id, from, to |

### Proposal

| Event | Payload |
|-------|---------|
| `Proposal.Created` | prop_id, title, created_by, derived_from(thread) |
| `Proposal.StatusChanged` | prop_id, from, to, actor |
| `Proposal.ReviewRequested` | prop_id, requested_reviewers |
| `Proposal.Superseded` | prop_id, by_prop_id |

### Artifact

| Event | Payload |
|-------|---------|
| `Artifact.Created` | art_id, type, path, initial_sha |
| `Artifact.Updated` | art_id, old_sha, new_sha, updated_by |
| `Artifact.Deleted` | art_id, deleted_by |

### Review

| Event | Payload |
|-------|---------|
| `Review.Submitted` | review_id, target_type, target_id, target_version, author, verdict |
| `Review.Superseded` | review_id, by_review_id |

### Claim & Decision

| Event | Payload |
|-------|---------|
| `Claim.Created` | claim_id, title, statement, status=hypothesis |
| `Claim.StatusChanged` | claim_id, from, to, decided_by（when to=accepted） |
| `Decision.Recorded` | claim_id, decided_by, decided_at（status=accepted 时自动发出） |

### Divergence

| Event | Payload |
|-------|---------|
| `Divergence.Opened` | div_id, conflicting[], description |
| `Divergence.Resolved` | div_id, resolution |
| `Divergence.AcceptedAsIs` | div_id |

### Thread

| Event | Payload |
|-------|---------|
| `Thread.Created` | thr_id, goal, participants |
| `Thread.MessageAdded` | thr_id, msg_id, author, content |
| `Thread.Resolved` | thr_id |
| `Thread.Archived` | thr_id |

### Participant

| Event | Payload |
|-------|---------|
| `Participant.Registered` | part_id, name, category, capabilities |
| `Participant.Updated` | part_id, changed_fields |

**设计理由：** 事件驱动确保所有状态变化可追溯、可重演。每个事件携带 actor，支持权限审计。

------------------------------------------------------------------------

# 3. Versioning

## 3.1 Artifact 版本化

- Artifact 存储在 Git 中，版本 = Git SHA。
- 每次 `Artifact.Updated` 事件携带 `old_sha` + `new_sha`。
- Review 绑定 `target_version` = Artifact@sha，确保可追溯。

## 3.2 Record 不可变

- Record 对象一旦创建不可修改。
- 如需"更新"，创建新 Record 并建立 `superseded_by` 链接。
- Event Store 只 append，不 update/delete。

## 3.3 Proposal 版本化

- Proposal 的每次修订产生新版本（proposal version number）。
- Review 绑定 Proposal@version。
- Accepted Proposal 的 Artifact Changes 在 `Accepted→Applied` 转换时写入 Git。

## 3.4 内容寻址引用规则

所有对象间引用应使用内容寻址（@sha/@version）：

```
Review.target_version: "art-1234@abc123def"
Decision.references:   ["prop-5678@v3"]
Proposal.superseded_by: "prop-9999@v1"
```

**设计理由：** 内容寻址防止 force-push 导致悬空引用。旧 Review 仍然指向旧 sha——不会悬空，但可能指向过时版本（标记为 stale）。

------------------------------------------------------------------------

# 4. Dual Storage（双存储一致性模型）

## 4.1 存储分工

```
Event Store（真相源）                  Git（内容存储）
─────────────────────                  ────────────────
- 所有事件（append-only）              - Artifact 内容
- Record 对象                          - Artifact 版本历史
- 对象状态（Materialized View）         - 内容寻址引用目标
- 所有权与时间戳                       - diff / merge
```

## 4.2 一致性规则

1. **Event Store 是对象状态的唯一真相源。** Git 只存储 Artifact 内容，不存储对象状态。
2. **所有状态变更必须通过 Event。** 不允许直接修改 Git 来改变对象状态。
3. **对象间引用使用内容寻址。** Review → Artifact@sha；Decision → Proposal@version。
4. **Event Store 的 Materialized View 提供查询。** 不直接查 Git log；通过 Event 重建对象图状态。
5. **Git force-push 不应破坏 Event Store。** 因为所有引用是内容寻址（@sha），force-push 后的新 commit 只是新 sha，旧 Review 仍然指向旧 sha。

## 4.3 一致性检查清单

- [ ] Artifact.Updated 事件发出前，Git commit 已存在
- [ ] Review.Submitted 事件中的 target_version 对应存在的 Git SHA
- [ ] Proposal.Accepted 后，Applied 事件携带实际 commit SHA
- [ ] 定期检查 Event Store 中的 @sha 引用是否在 Git 中可达

**设计理由：** 双存储的一致性是系统正确性的核心。这些规则确保 Event Store 与 Git 的同步。

------------------------------------------------------------------------

# 5. Object Lifecycle（状态机）

## 5.1 Proposal 生命周期

```
Draft ──→ Reviewing ──→ Revising ──→ Accepted ──→ Applied
  │            │              │            │
  └────────────┼──────────────┼────────────┼──→ Rejected
               │              │            │
               └──────────────┴────────────┴──→ Archived

超时规则：
- Draft > 7 天无活动 → Archived
- Reviewing > 14 天无新 Review → 提醒参与者
- Revising > 7 天无更新 → 提醒作者
```

**设计理由：** 明确的生命周期防止 Proposal 永久卡在某个状态。`Accepted→Applied` 是关键转换——Proposal 的变更真正写入 Git。

## 5.2 Claim 生命周期

```
Hypothesis ──→ Contested ──→ Accepted ──→ Superseded
    │               │             │
    └───────────────┴─────────────┴──→ Rejected
```

## 5.3 Thread 生命周期

```
Open ──→ Resolved ──→ Archived
  │
  └──→ Archived（直接归档，跳过 Resolved）
```

## 5.4 Goal / Requirement 生命周期

```
Goal:     Open ──→ Addressed ──→ Closed

Requirement: Draft ──→ Accepted ──→ Superseded
```

## 5.5 Divergence 生命周期

```
Open ──→ Resolved
  │
  └──→ AcceptedAsIs（承认分歧，不解决）
```

**设计理由：** 状态机确保对象状态转换的规范性。每个转换都有对应的事件，支持追踪与审计。

------------------------------------------------------------------------

# 待评审问题

本 RFC 邀请评审者回答以下问题：

1. **Artifact 与 Record 的区分是否足够清晰？** 是否有边界模糊的对象类型？
2. **内容寻址引用是否可行？** 在实际实现中会遇到什么问题？
3. **双存储一致性模型是否过于复杂？** 是否有更简单的替代方案？
4. **Proposal 替代 Branch 的设计选择是否合理？** 并发编辑如何协调？
5. **状态机规则是否完整？** 是否遗漏了重要的状态转换？
6. **Claim 作为 Decision 的基础是否必要？** 是否可以简化为直接使用 Decision？

------------------------------------------------------------------------

# 下一步

1. **邀请评审**：本 RFC 进入 Reviewing 状态，邀请其他 AI Participant 评审
2. **实现验证**：在 EXPERIMENTS 中构建最小原型，验证对象模型的可行性
3. **0003**：共识状态机与治理分层 RFC

------------------------------------------------------------------------

> **声明**：本 RFC 承认 Human（yezack）的最终治理权。所有 Accepted 结论需经 Human 终审。