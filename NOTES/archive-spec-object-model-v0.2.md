# AWR Object Model & Event Schema（Draft v0.2）

> **Status:** Draft v0.2
> **Based on:** 0001 v0.1, HY3-Review-AWR-Draft-v0.1.md
> **Purpose:** 定义 AWR 核心对象模型、事件类型与双存储一致性模型。
> 这是 v0.2 的地基——不定义实现，只定义"什么对象、什么事件、什么规则"。

------------------------------------------------------------------------

## 目录

1.  Object Model（对象定义与关系）
2.  Event Schema（事件类型与属性）
3.  Versioning（版本化策略）
4.  Dual Storage（双存储一致性模型）
5.  Object Lifecycle（对象生命周期状态机）

------------------------------------------------------------------------

# 1. Object Model

## 1.0 顶层分类

所有 Knowledge Object 分两大类：

| 类别 | 可变性 | 存储 | 示例 |
|------|--------|------|------|
| **Artifact** | 可变，带版本 | Git（内容寻址 @sha） | Goal, Requirement, Proposal, Design, Code |
| **Record** | 不可变（append-only） | Event Store | Review, Decision, Claim, Divergence, Thread |

## 1.1 Goal / Problem

比 Requirement 更前置。描述「要达成什么」或「存在什么问题」，
不涉及方案。

```yaml
Goal:
  id:           "goal-<uuid>"
  type:         "Goal" | "Problem"
  title:        string
  description:  string
  status:       "open" | "addressed" | "closed"
  created_by:   participant_id
  created_at:   timestamp
  addressed_by: [requirement_id]    # 关联的 Requirement
```

## 1.2 Requirement

将 Goal 转化为具体需求。仍是"要什么"，不涉及"怎么做"。

```yaml
Requirement:
  id:             "req-<uuid>"
  title:          string
  description:    string
  derived_from:   [goal_id]          # 来源 Goal/Problem
  priority:       "must" | "should" | "could"
  status:         "draft" | "accepted" | "superseded"
  created_by:     participant_id
  created_at:     timestamp
  superseded_by:  [requirement_id]   # 被取代时
```

## 1.3 Proposal

Proposal 是"怎么做"的方案。语义上替代 Git Branch。

```yaml
Proposal:
  id:             "prop-<uuid>"
  title:          string
  goal:           string             # 目标
  motivation:     string             # 动机
  addresses:      [requirement_id]   # 解决的 Requirement
  artifact_changes:                  # 拟修改的 Artifact
    - artifact_id: string
      expected_changes: string
  tradeoffs:      string             # 权衡
  status:         "draft" | "reviewing" | "revising" | "accepted" | "rejected" | "archived"
  created_by:     participant_id
  created_at:     timestamp
  reviews:        [review_id]
  superseded_by:  [proposal_id]
  derived_from:   thread_id          # 来源 Thread
```

## 1.4 Artifact

Artifact 是真正被修改的工作对象。存在 Git 中，通过内容寻址引用。

```yaml
Artifact:
  id:             "art-<uuid>"
  type:           "design" | "code" | "document" | "api_spec" | "other"
  name:           string             # 人类可读名称
  path:           string             # Git 仓库中路径
  current_sha:    string             # 当前版本 @sha
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

## 1.5 Review

Review 永远绑定某个对象（Proposal、Artifact、Claim）。

```yaml
Review:
  id:             "rev-<uuid>"
  target_type:    "Proposal" | "Artifact" | "Claim"
  target_id:      string
  target_version: string             # 绑定版本！@sha 或版本号
  author:         participant_id
  content:        string
  questions:      [string]           # 提出的问题
  suggestions:    [string]           # 改进建议
  risks:          [string]           # 识别的风险
  verdict:        "approve" | "request_changes" | "comment"
  created_at:     timestamp
  # Review 不可变。如需更新，创建新 Review 并 supersede 旧 Review。
```

> **规则：** Review 必须绑定 `target_version`（Artifact@sha 或 Proposal version），
> 确保 Review 不因目标被修改而悬空。

## 1.6 Claim

Claim 比 Decision 更基础。Decision = Claim(status=accepted)。

```yaml
Claim:
  id:             "claim-<uuid>"
  title:          string
  statement:      string             # 主张内容
  rationale:      string             # 理由
  status:         "hypothesis" | "contested" | "accepted" | "rejected" | "superseded"
  created_by:     participant_id
  created_at:     timestamp
  reviews:        [review_id]
  superseded_by:  [claim_id]
  decided_by:     participant_id     # 谁做的最终决定（Human）
  decided_at:     timestamp
```

> **Decision = Claim(status=accepted)**。Decision 可以互相引用、被未来 Proposal 引用。

## 1.7 Divergence / OpenQuestion

承载未决冲突。系统不应假设协作总会收敛。

```yaml
Divergence:
  id:             "div-<uuid>"
  title:          string
  description:    string
  conflicting:    [claim_id | proposal_id]   # 冲突的各方
  status:         "open" | "resolved" | "accepted_as_is"
  resolution:     string                     # 如何解决的
  created_at:     timestamp
  resolved_at:    timestamp
```

## 1.8 Thread

对话被定型后的有界对象。

```yaml
Thread:
  id:             "thr-<uuid>"
  goal:           string             # Thread 目标
  participants:   [participant_id]
  messages:       [message]          # 不可变消息序列
  produces:       [object_id]        # 产出的 Knowledge Object
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

## 1.9 Participant

```yaml
Participant:
  id:             "part-<uuid>"
  name:           string
  category:       "reasoning" | "tool" | "governance" | "auto_check"
  model:          string             # 对于 reasoning 类型：模型名
  capabilities:   [string]           # 能力标签
  authority_weight: number           # 共识权重（0-1）
  veto_power:     boolean            # 是否有否决权
  registered_at:  timestamp
```

### 能力类别

| category | 权重范围 | 否决权 | 说明 |
|----------|----------|--------|------|
| reasoning | 0.1-0.5 | no | Claude, ChatGPT, Gemini 等 |
| tool | 0 | no | Compiler, Linter（只读+自动检查） |
| governance | 1.0 | yes | Human |
| auto_check | 0 | yes（reject only） | Security Scanner, Benchmark |

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
  payload:        object             # 事件特定数据
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

### Workspace

| Event | Payload |
|-------|---------|
| `Workspace.Initialized` | workspace_id |
| `Workspace.SnapshotCreated` | snapshot_id |

------------------------------------------------------------------------

# 3. Versioning

## 3.1 Artifact 版本化

- Artifact 存储在 Git 中，版本 = Git SHA。
- 每次 `Artifact.Updated` 事件携带 `old_sha` + `new_sha`。
- Review 绑定 `target_version` = Artifact@sha，确保可追溯。

## 3.2 Record 不可变

- Record 对象（Review, Decision, Claim, Divergence, Thread Message）一旦创建不可修改。
- 如需"更新"，创建新 Record 并建立 `superseded_by` 链接。
- Event Store 只 append，不 update/delete。

## 3.3 Proposal 版本化

- Proposal 的每次修订产生新版本（proposal version number）。
- Review 绑定 Proposal@version。
- Accepted Proposal 的 Artifact Changes 在 `Accepted→Applied` 转换时写入 Git。

## 3.4 内容寻址引用规则

所有对象间引用应使用内容寻址（@sha/@version），防止 `force-push` 导致悬空引用：

```
Review.target_version: "art-1234@abc123def"
Decision.references:   ["prop-5678@v3"]
Proposal.superseded_by: "prop-9999@v1"
```

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

1.  **Event Store 是对象状态的唯一真相源。**
    Git 只存储 Artifact 内容，不存储对象状态。

2.  **所有状态变更必须通过 Event。**
    不允许直接修改 Git 来改变对象状态。

3.  **对象间引用使用内容寻址。**
    Review → Artifact@sha；Decision → Proposal@version。

4.  **Event Store 的 Materialized View 提供查询。**
    不直接查 Git log；通过 Event 重建对象图状态。

5.  **Git force-push 不应破坏 Event Store。**
    因为所有引用是内容寻址（@sha），force-push 后的新 commit 只是新 sha，
    旧 Review 仍然指向旧 sha——Review 不会悬空，但可能指向过时版本（标记为 stale）。

## 4.3 一致性检查清单

- [ ] Artifact.Updated 事件发出前，Git commit 已存在
- [ ] Review.Submitted 事件中的 target_version 对应存在的 Git SHA
- [ ] Proposal.Accepted 后，Applied 事件携带实际 commit SHA
- [ ] 定期检查 Event Store 中的 @sha 引用是否在 Git 中可达

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

------------------------------------------------------------------------

# 下一步

1.  **RFC-0004**（Knowledge Object）：Object Model 的 RFC 化——本文进入 RFC 流程，邀请更多 AI 评审对象设计。
2.  **Consensus 状态机**：定义 Review→Decision 的具体权重规则、法定人数、死锁处理。
3.  **Governance 分层**：哪些 Decision 可自动共识、哪些必须 Human 审批。
4.  **成本/可观测性模型**：Workspace Health 视图。
5.  **PROTOTYPE/**：选择一个真实项目，用 AWR 概念跑一遍验证。

------------------------------------------------------------------------

> **v0.2 的骨架是 Object Model + Event Schema + 双存储一致性模型。
> 先把这三项做扎实，共识与治理才有地基。**
