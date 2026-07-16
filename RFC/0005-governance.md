# AWR RFC-0005 — Governance (Draft v0.1)

> **Status:** Draft
> **Version:** v0.1
> **Reviewers:** 待定（邀请所有 AI Participant）
> **Based on:** [RFC-0001](../RFC/0001-conversation-trap.md), [RFC-0002 Workspace](../RFC/0002-workspace.md), [RFC-0003 Participant](../RFC/0003-participant.md), [NOTES/HY3-Review-AWR-Draft-v0.1.md](../NOTES/HY3-Review-AWR-Draft-v0.1.md)
> **Supersedes:** 无
> **Purpose:** 定义 AWR 的共识状态机规则与治理分层模型（Participant 权威权重体系见 RFC-0003）。

------------------------------------------------------------------------

## 变更记录

| 版本 | 变更 |
|------|------|
| v0.1 | 初始草案 |

------------------------------------------------------------------------

# 为什么写这份 RFC？

RFC-0001 确立了「Human Governance」原则，RFC-0004 定义了对象模型（RFC-0002 定义 Workspace 与双存储）。但两者都没有回答一个关键问题：

> **当多个 Participant 产生分歧时，如何达成共识？**

本 RFC 填补这个空白：定义共识状态机、治理分层、以及权威权重体系。

没有共识机制，AWR 的对象模型只是一个静态的数据结构，无法支持真正的协作。

------------------------------------------------------------------------

# 核心主张

> **共识不是多数表决，而是基于权威权重的分层决策。**

本 RFC 提出以下设计选择：

1. **权威权重体系**：Participant 按能力类别拥有不同的共识权重
2. **治理分层**：不同类型的 Decision 有不同的审批要求（自动 / AI 审批 / Human 终审）
3. **共识状态机**：明确的 Proposal→Review→Decision 流程规则（法定人数、超时、死锁处理）
4. **分歧显式化**：Divergence 对象承载未决冲突，不强制收敛

------------------------------------------------------------------------

# 1. Participant 权威权重体系

## 1.1 权重分配原则

每个 Participant 拥有一个 `authority_weight`（0-1）和 `veto_power`（是否有否决权）。

| 类别 | 权重范围 | 否决权 | 说明 |
|------|----------|--------|------|
| reasoning | 0.1-0.5 | no | Claude, ChatGPT, Gemini 等推理型 AI |
| tool | 0 | no | Compiler, Linter（只读+自动检查） |
| governance | 1.0 | yes | Human |
| auto_check | 0 | yes（reject only） | Security Scanner, Benchmark |

**设计理由：**

- **reasoning**: 权重根据模型能力和领域专长分配。同一领域的多个 AI 权重总和不超过 1.0。
- **tool**: 工具型 Participant 不参与共识投票，但可以提供客观检查结果。
- **governance**: Human 拥有最高权重（1.0）和否决权，确保最终治理权。
- **auto_check**: 安全扫描器、性能基准等可以否决 Proposal（reject only），但不能批准。

## 1.2 权重计算示例

假设一个工作区有以下 Participant：

| Participant | 类别 | 权重 | 否决权 |
|-------------|------|------|--------|
| Human (yezack) | governance | 1.0 | yes |
| Claude 3.5 | reasoning | 0.3 | no |
| ChatGPT 4o | reasoning | 0.3 | no |
| Code Linter | tool | 0 | no |
| Security Scanner | auto_check | 0 | yes |

**总权重：** 1.0 + 0.3 + 0.3 + 0 + 0 = 1.6

## 1.3 权重动态调整

权重不是固定的，可以通过以下机制调整：

1. **领域权重**：在特定领域（如安全、性能），相关 Participant 的权重临时提升
2. **历史表现**：基于过去的 Review 质量和 Decision 正确性动态校准
3. **Human 干预**：Human 可以手动调整任何 Participant 的权重

**设计理由：** 不同任务需要不同的权威配置。例如，安全相关的 Proposal 应给予 Security Scanner 更高权重。

------------------------------------------------------------------------

# 2. 治理分层模型

## 2.1 Decision 类型与审批要求

| Decision 类型 | 审批要求 | 说明 |
|---------------|----------|------|
| **Auto-consensus** | 无需审批 | 工具型 Participant 的自动检查通过即可 |
| **AI Approval** | 推理型 AI 审批 | Proposal 获得足够权重的 AI Reviewer 批准 |
| **Human Review** | Human 必须审查 | 高风险、高影响的 Proposal |
| **Human Approval** | Human 必须批准 | 关键决策、架构变更 |

## 2.2 治理分层规则

```
Proposal 提交
    │
    ├──→ [自动检查] Security Scanner / Linter
    │       │
    │       ├──→ 失败 → Rejected
    │       │
    │       └──→ 通过 → 进入共识流程
    │
    ├──→ [AI 审批层] 推理型 Participant Review
    │       │
    │       ├──→ 权重 >= 阈值（默认 0.6）→ AI Approved
    │       │
    │       └──→ 权重 < 阈值 → 需要 Human 介入
    │
    ├──→ [Human 审批层] Human Review/Approval
    │       │
    │       ├──→ Approved → Accepted
    │       │
    │       └──→ Request Changes / Rejected
    │
    └──→ [最终决策] Decision.Recorded
```

## 2.3 分层阈值配置

```yaml
governance:
  thresholds:
    ai_approval: 0.6           # AI 审批权重阈值
    human_review_required:     # 需要 Human Review 的情况
      - artifact_type: "code"
        change_size: "large"   # 代码变更超过 1000 行
      - artifact_type: "api_spec"
      - proposal_category: "architecture"
    human_approval_required:   # 需要 Human Approval 的情况
      - artifact_type: "code"
        change_size: "xlarge"  # 代码变更超过 5000 行
      - proposal_category: "security"
      - proposal_category: "license"
```

**设计理由：** 治理分层解决「机器速度的治理」问题——低风险的自动共识，高风险的 Human 终审。

## 2.4 Human 终审权

Human 始终保留以下权力：

1. **否决权**：可以否决任何 AI Approved 的 Proposal
2. **批准权**：可以批准任何被 AI 拒绝的 Proposal
3. **重审权**：可以要求重新 Review 任何 Decision
4. **权重调整权**：可以调整任何 Participant 的权重

**设计理由：** 这是 DP-4 (Human Governance) 的具体体现。

------------------------------------------------------------------------

# 3. 共识状态机

## 3.1 Proposal 共识流程

```
Draft ──→ Reviewing ──→ Revising ──→ Accepted ──→ Applied
  │            │              │            │
  └────────────┼──────────────┼────────────┼──→ Rejected
               │              │            │
               └──────────────┴────────────┴──→ Archived

Reviewing 阶段的状态转换：
    Reviewing
      │
      ├──→ [权重 >= 阈值] → AI Approved
      │       │
      │       └──→ [需要 Human Review] → 等待 Human
      │             │
      │             └──→ Human Approved → Accepted
      │
      ├──→ [否决权触发] → Rejected（Security Scanner reject）
      │
      ├──→ [超时] → 提醒参与者 / 自动 Escalate 到 Human
      │
      └──→ [分歧检测] → Divergence.Opened
```

## 3.2 法定人数规则

| 场景 | 法定人数要求 |
|------|-------------|
| AI Approval | 至少 2 个 reasoning-type Participant 的 Review |
| Human Review | 至少 1 个 governance-type Participant 的 Review |
| Auto-consensus | 所有 auto_check Participant 通过 |

**设计理由：** 防止单个 Participant 垄断决策。

## 3.3 超时规则

| 状态 | 超时时间 | 超时行为 |
|------|----------|----------|
| Draft | 7 天 | 自动 Archived |
| Reviewing | 14 天 | 提醒所有参与者；超过 21 天自动 Escalate 到 Human |
| Revising | 7 天 | 提醒作者；超过 14 天自动 Rejected |
| Waiting for Human | 3 天 | 提醒 Human；超过 7 天自动 Escalate 到上级 |

**设计理由：** 防止 Proposal 永久卡在某个状态。

## 3.4 死锁处理

当共识陷入死锁（如两个高权重 AI 互相否决），系统采取以下策略：

1. **自动检测**：连续 3 次 Review 结果互相矛盾 → 死锁检测
2. **权重调整**：临时提升 governance-type Participant 的权重
3. **Human Escalation**：自动通知 Human 介入
4. **超时机制**：超过阈值时间未达成共识 → 强制 Escalate

**设计理由：** 死锁是协作系统的常见问题，必须有明确的处理规则。

## 3.5 分歧处理

当 Review 结果出现明显分歧时：

1. **Divergence.Opened**：创建 Divergence 对象，记录冲突各方
2. **分歧分析**：委托 Reviewer Participant 分析分歧原因
3. **Resolution Proposal**：创建新 Proposal 解决分歧
4. **AcceptedAsIs**：如果分歧无法解决，Human 可以选择「承认分歧」

**设计理由：** 系统不应假设协作总会收敛。Divergence 让异议显式化。

------------------------------------------------------------------------

# 4. Review 与 Verdict 规则

## 4.1 Review Verdict 类型

| Verdict | 权重贡献 | 说明 |
|---------|----------|------|
| approve | +participant.weight | 批准 Proposal |
| request_changes | 0 | 请求修改，不贡献权重 |
| comment | 0 | 仅评论，不参与投票 |

**设计理由：** 只有明确的 approve 才贡献权重，request_changes 和 comment 不参与共识计算。

## 4.2 Review 绑定规则

Review 必须绑定目标对象的具体版本：

```
Review.target_version: "prop-123@v2"
```

**设计理由：** 确保 Review 不因目标被修改而悬空。

## 4.3 Review 时效性

Review 在以下情况标记为 stale：

1. **目标版本变更**：Artifact 被更新到新的 SHA
2. **时间过期**：Review 创建超过 30 天
3. **新 Review 提交**：同一目标的新 Review 会使旧 Review 过期

**设计理由：** 确保 Review 反映最新状态。

------------------------------------------------------------------------

# 5. Decision 生命周期

## 5.1 Decision 创建规则

Decision 只能在以下条件下创建：

1. **AI Approved**：Proposal 获得足够权重的 AI Review
2. **Human Approved**：Human 明确批准
3. **Auto-consensus**：所有自动检查通过且无需 Human 审批

## 5.2 Decision 状态转换

```
Proposed ──→ Accepted ──→ Implemented ──→ Superseded
    │               │
    └───────────────┴──→ Rejected
```

## 5.3 Decision 引用规则

Decision 可以被以下对象引用：

- **Proposal**：引用相关 Decision 作为依据
- **Claim**：引用 Decision 支持主张
- **Artifact**：引用 Decision 说明设计理由

所有引用使用内容寻址：

```
Decision.references: ["prop-5678@v3", "claim-123@accepted"]
```

------------------------------------------------------------------------

# 待评审问题

本 RFC 邀请评审者回答以下问题：

1. **权重体系是否合理？** reasoning-type Participant 的权重范围（0.1-0.5）是否恰当？
2. **治理分层是否足够？** 是否遗漏了重要的审批层次？
3. **超时规则是否合理？** 14 天的 Reviewing 超时是否太长/太短？
4. **死锁处理是否足够？** 是否需要更复杂的死锁检测机制？
5. **Divergence 是否必要？** 是否可以简化为直接升级到 Human？
6. **Review 时效性规则是否合理？** 30 天的过期时间是否恰当？

------------------------------------------------------------------------

# 下一步

1. **邀请评审**：本 RFC 进入 Reviewing 状态，邀请其他 AI Participant 评审
2. **实现验证**：在 EXPERIMENTS 中构建共识状态机原型
3. **细化规则**：根据评审意见调整阈值、超时时间等参数

------------------------------------------------------------------------

> **声明**：本 RFC 承认 Human（yezack）的最终治理权。所有 Accepted 结论需经 Human 终审。