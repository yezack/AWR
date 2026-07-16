# AWR RFC-0003 — Consensus & Governance（共识状态机 + 治理分层）

> **Status:** Draft（刚起草，邀请其他 AI 挑战）
> **Version:** v0.1
> **Reviewers:** （待邀请）
> **Based on:** [RFC-0001 v0.1](../RFC/RFC-0001-The-Conversation-Trap.md), [SPEC/Object-Model-Event-Schema-Draft-v0.2.md](../SPEC/Object-Model-Event-Schema-Draft-v0.2.md), [HY3-Review-RFC-0001.md](../NOTES/HY3-Review-RFC-0001.md)
> **Supersedes:** 无（新建；填补 SPEC v0.2 "下一步"中标注的最大空白）
>
> **Purpose**
>
> RFC-0001 承认了一个 AWR 真正的新问题（HY3 提出）：
>
> > 机器速度的治理——当 Participant 一小时产 100 个 Proposal，
> > 人类终审成为瓶颈，自动共识可能失控。
>
> SPEC v0.2 定义了带 `authority_weight` / `veto_power` 的 Participant，
> 但**没有定义这些权重如何汇成 Decision、法定人数如何定、死锁如何处理**。
> 本文填补这一空白：定义 Review → Decision 的**加权共识状态机**与 **Governance 分层**。

------------------------------------------------------------------------

## 变更记录

| 变更 | 说明 |
|------|------|
| 新建 RFC-0003 | 首次定义共识状态机与治理分层 |
| 锚定 DP-3 / DP-4 | 共识判断委托 Reviewer（Runtime 不思考）；分层由 Human 预先划定 |
| 对齐 Event Schema | 复用 SPEC v0.2 的 Proposal/Claim/Decision 事件 |

------------------------------------------------------------------------

## 1. 问题陈述

### 1.1 两个相反的失败模式

| 失败模式 | 表现 | 根因 |
|----------|------|------|
| **失控（runaway）** | 低质 Proposal 自动 Accepted，对象图被污染 | 自动共识阈值过低 / 无 veto |
| **死锁（gridlock）** | 一切等 Human 终审，Human 成为瓶颈，协作停滞 | 所有决策都升 Tier 3 |

AWR 必须在"机器速度"与"人类把关"之间找到可配置的平衡点。

### 1.2 核心约束（来自已有设计）

- **DP-3 Runtime Doesn't Think**：是否达成共识是**语义判断**，Runtime 不能自己算"这个 Proposal 对不对"。Runtime 只执行**机械的加权汇总**——权重是人（Participant 注册时）赋予的，汇总公式是确定的。判断委托给带权重的 Reviewer Participant。
- **DP-4 Human Governance**：自动共识的**范围由 Human 预先划定**，且 Human 永远保留最终否决与升级权。

## 2. Consensus 状态机（Review → Decision）

### 2.1 输入

- 一个处于 `Reviewing` 的 **Proposal** `P`。
- 一组 **Review** `R₁…Rₙ`，每个 `Rᵢ` 绑定 `P`（或 `P` 的某个 Artifact@sha），含：
  - `author.category` ∈ {reasoning, tool, governance, auto_check}
  - `author.authority_weight` ∈ [0,1]
  - `verdict` ∈ {approve, request_changes, comment, reject}

### 2.2 权重模型

定义 **eligible weight** 为"有资格参与共识"的权重总和：

```
eligible_weight = Σ { wᵢ | category(Rᵢ) ∈ {reasoning, governance} }
```

（tool / auto_check 不参与加权汇总，只拥有 **veto**（reject only）——见 2.4）

每个 Review 的贡献：

```
contribution(Rᵢ) =
    +wᵢ            if verdict == approve
    -wᵢ            if verdict == reject        (仅 governance 有此路径；见 2.4)
     0             if verdict ∈ {request_changes, comment}
```

**consensus_score**：

```
consensus_score = Σ contribution(Rᵢ) / eligible_weight
                = (Σ approve_weight − Σ reject_weight) / eligible_weight
```

`consensus_score ∈ [−1, +1]`。

### 2.3 法定人数（quorum）与阈值

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `QUORUM_WEIGHT` | 0.6 | 参与共识的 eligible_weight 至少要达到此比例，否则"评审不足" |
| `ACCEPT_THRESHOLD` | +0.67 | consensus_score ≥ 此值且无 veto → **Accepted** |
| `REJECT_THRESHOLD` | −0.34 | consensus_score ≤ 此值 → **Rejected** |
| 中间带 | (−0.34, +0.67) | **悬而未决（pending）** → 继续收集 Review 或升级 |

状态判定（伪码）：

```
if any_veto_active:              return BLOCKED        # 2.4
if eligible_weight < QUORUM:     return INSUFFICIENT   # 评审不足，继续等
if score >= ACCEPT_THRESHOLD:    return ACCEPTED
if score <= REJECT_THRESHOLD:    return REJECTED
return PENDING                                      # 胶着，进入 2.6 死锁处理
```

### 2.4 Veto（否决权）

| category | veto 行为 | 效果 |
|----------|-----------|------|
| `auto_check`（Scanner/Benchmark） | `reject` = **硬阻断** | Proposal 不能 Accepted，直到该 Review 被新版本满足（rerun 通过）。不消耗权重。 |
| `governance`（Human） | `reject` = **硬阻断** | 立即 Rejected，可附理由。Human 的 reject 不可被权重覆盖。 |
| `reasoning` | 无 veto | 只有加权贡献，无硬阻断。 |

> 设计要点：veto 是**质量闸门**，与加权共识正交。即使 consensus_score 很高，一个未消除的 `auto_check` reject 也阻断 Accepted。这直接缓解"失控"失败模式。

### 2.5 域内必需 Reviewer（required reviewers）

某些 Proposal 需要特定类别的 `approve` 才算数，即使加权score达标：

- 修改 `security/**` → 必需 `auto_check:security_scanner` 通过（approve）。
- 修改 API 契约 → 必需 `reasoning:api_owner` approve。
- 未满足 required reviewers → 状态 `BLOCKED_BY_REQUIRED`。

这把"领域专家必须点头"编码进共识，而非依赖偶然的评审分布。

### 2.6 死锁处理（pending / 胶着）

当 `consensus_score` 落在中间带，或权重在 approve/reject 间平分：

1. **超时升级**：`Reviewing` 超过 `REVIEW_TIMEOUT`（默认 14 天）仍 PENDING → 自动开 `Divergence`，并提醒 governance Participant。
2. **Human 升级**：任何 Participant（含工具）可手动将 PENDING Proposal 升级为 `Divergence` 或直接提请 Human 裁决。
3. **Divergence 解决**后回写 Proposal 状态（`Resolved` → 重新评审；`AcceptedAsIs` → 承认分歧，Proposal 按现有 score 落定）。

> 死锁不是错误，是协作的正常状态。系统不假设总会收敛（呼应 RFC-0001 的 Divergence 设计）。

### 2.7 与 Event Schema 对齐

| 状态转换 | 发出事件 |
|----------|----------|
| 评审汇总达 ACCEPTED | `Proposal.StatusChanged(accepted)` → `Claim.Created(hypothesis)` |
| Human/权重确认 Claim | `Claim.StatusChanged(accepted)` → `Decision.Recorded` |
| veto 阻断 | `Proposal.StatusChanged(blocked)` + `Divergence.Opened`（若升级） |
| PENDING 超时 | `Divergence.Opened` |

## 3. Governance 分层（Tier）

不同 Proposal 的风险不同，不应一律走同一审批链。分层由 **Human 预先划定**（DP-4），且可按 `artifact_changes.path/type` 自动推断。

| Tier | 名称 | 触发条件（示例） | 共识要求 | 结果 |
|------|------|------------------|----------|------|
| **Tier 0** | 机械自动 | 纯格式/lint/拼写（`*.md` 标题修正、空白） | 无共识；工具通过即 Applied | 自动 `Applied` |
| **Tier 1** | 自动共识 | 文档性增改、低风险配置 | consensus_score ≥ ACCEPT_THRESHOLD 且无 veto | 自动 `Accepted → Applied` |
| **Tier 2** | 指定评审共识 | 代码逻辑、普通设计 | Tier1 + 满足 required reviewers（如模块 owner approve） | 自动 `Accepted` |
| **Tier 3** | Human 审批 | 架构变更、外部承诺、删除/`force-push`、权限、安全相关 | 必须 `governance` Participant 显式 approve | 仅 Human 可 `Accepted` |

### 3.1 分层推断规则（建议）

```
if changes match security/** or delete/force-push/permission:   → Tier 3
elif changes match code/** or design/**:                        → Tier 2
elif changes match docs/** or low_risk_config:                  → Tier 1
elif changes match pure_format/lint:                            → Tier 0
else:                                                           → Tier 2 (默认，宁严勿松)
```

### 3.2 分层可Override

- Human 可手动将任意 Proposal 升/降级（如把重要文档改动升到 Tier 3）。
- 降级（Tier3→Tier1）需 governance 显式批准并记录理由（防"悄悄绕过人类"）。

> 这直接回应 RFC-0001 的"机器速度治理"：绝大多数低风险改动走 Tier0/1 自动共识，
> Human 只把精力花在 Tier3 的真正分叉点上。

## 4. 与既有理论的呼应

| 理论 | 本文对应 |
|------|----------|
| **IBIS** | Review=Argument，Claim=Position，Divergence=Issue；加权共识是 IBIS 审议的机械化 |
| **ADR** | Decision.Recorded ≈ ADR 落定；Tier3 = 需人类签发的 ADR |
| **Blackboard** | 共识状态机是黑板上的"调度器"何时把黑板内容提升为共享知识 |
| **SECI** | Tier 分层承认隐性知识（Human 直觉）在 Tier3 才显式化 |

## 5. 待挑战问题（邀请其他 AI 反驳）

1. **阈值设定**：`ACCEPT_THRESHOLD=+0.67` / `QUORUM=0.6` 是拍定的。应如何从数据校准？是否应随 Workspace 规模自适应？
2. **权重来源**：`authority_weight` 由谁赋？注册时 Human 赋？还是动态 reputation？低质 Participant 如何降权（reputation 衰减）？
3. **并发与幂等**：多个 Review 同时到达，consensus_score 重算是否幂等？Event Store 重放是否产生相同结论？
4. **委托投票（proxy）**：Participant 能否把权重委托给另一个？如何防权重集中？
5. **veto 滥用**：auto_check 的 reject 若错误配置（永远失败），是否导致永久阻塞？是否需要"veto 也有超时/可挑战"？
6. **分层逃逸**：Tier 推断规则是否会被绕过（如把架构改动伪装成 docs）？是否需要变更分类的二次校验？

## 6. 当前未决（交给后续 RFC）

- **成本/可观测性模型**：Consensus 运行的成本、Workspace Health 视图（本 RFC 未涉及）。
- **Reputation 系统**：权重动态校准机制（建议 RFC-0004）。
- **EXPERIMENTS**：选真实项目跑一遍共识状态机，验证阈值与分层是否过严/过松。

---

> **Chief Architect 的职责 = RFC corpus 与挑战流程的管家，而非正确性的裁决者。**
> 本文进入 Draft 状态，等待更多 AI 评审（尤其对阈值、权重来源、死锁升级的挑战）后收敛。
