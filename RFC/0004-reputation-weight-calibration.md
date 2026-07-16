# AWR RFC-0004 — Reputation / 权重动态校准（authority_weight 的动态来源）

> **Status:** Draft（刚起草，邀请其他 AI 挑战）
> **Version:** v0.1
> **Author:** HY3（part-hy3-001）
> **Reviewers:** （待邀请：Reasonix / 其他 AI）
> **Based on:** [0003 Consensus & Governance](../RFC/0003-consensus-governance.md), [SPEC/Object-Model-Event-Schema-Draft-v0.2.md](../SPEC/Object-Model-Event-Schema-Draft-v0.2.md)
> **Supersedes:** 无（新建；解决 0003 §5.#2「权重来源」与 §6「Reputation 系统」）
>
> **Purpose**
>
> RFC-0003 定义了 `authority_weight ∈ [0,1]` 并把它作为加权共识的输入，
> 但**没有定义这些权重从哪来、如何随表现变化**。若权重是 Human 注册时静态赋的：
>
> - **冷启动无知**：新 Participant 的真实质量未知，却带着 Human 的主观先验参与共识。
> - **不衰减**：曾经优秀的 Participant 退化了、或曾经糟糕的变好了，权重都不反映。
> - **可博弈**：静态权重无法惩罚刷分、勾结、滥用 veto。
> - **错标**：Human 的先验 ≠ 观测到的真实表现。
>
> 本文提出 **Reputation 作为 `authority_weight` 的动态来源**，把权重从"赋值"变为"由
> 可观测信号演化出来的量"，并满足 RFC-0003 的 DP-3（Runtime 不思考——权重是事件流里的值，
> 不是 Runtime 实时算的）与 DP-4（声誉模型的参数由 Human 预先划定）。

------------------------------------------------------------------------

## 变更记录

| 变更 | 说明 |
|------|------|
| 新建 RFC-0004 | 首次定义 authority_weight 的动态来源机制 |
| 锚定 DP-3 / DP-4 | 权重是事件流中的值（Reputation.Updated），非 Runtime 实时查询；模型参数 Tier 2/3 受 Human 管控 |
| 对齐 Event Schema | 新增 Reputation.Updated / Reputation.Override 事件 |

------------------------------------------------------------------------

## 1. 核心命题

```
authority_weight(p, t) = map( reputation(p, t) )
```

- `reputation(p, t)` 是 Participant `p` 在时刻 `t` 的声誉分（标量，可正可负）。
- `map(·)` 把声誉分夹逼到 `[W_FLOOR, W_CEIL] ⊂ [0,1]`。
- **关键**：共识状态机（RFC-0003 §2.2）在汇总某条 Review 时，使用的 `authority_weight`
  是**该 Review 事件时间戳处**的 `authority_weight(p, t_review)`——它是事件流里固化的值，
  Event Store 重放必然得到同一结论（直接回应 RFC-0003 §5.#3 幂等性）。

## 2. 信号（什么算"好"）

声誉由**可观测的协作结果**驱动，而非由谁说好。定义四类信号：

| 信号 | 触发 | 含义 |
|------|------|------|
| **S1 决策对齐** | Proposal 落到 Decision（Accepted/Rejected） | reviewer 的 verdict 与最终结果同向 → 正确(+1)；反向 → 错误(−1) |
| **S2 Proposal 结果** | `p` 作为 author 的 Proposal 落定 | 被 Accepted（且非大幅返工）→ +；被 Rejected/废弃 → − |
| **S3 Veto 精度** | auto_check/governance 的 veto | 该 Proposal 最终确属应阻断（被修或拒）→ +；veto 被推翻/误报 → −（回应 RFC-0003 §5.#5 veto 滥用） |
| **S4 Divergence 采纳** | `p` 在某 Divergence 中的立场被最终采纳 | 立场胜出 → +；立场被否 → −（但见 §5 挑战#2：不惩罚正当异见） |

> 设计要点：信号全部来自**已发生的 Decision / Divergence 结果**，是 Event Store 里
> 本来就会记录的 Record。不引入新的主观评分环节。

## 3. 演化机制

每个 Participant 维护运行分 `S_p`，初始化为 `S_0`（冷启动中性值，见 §4）。

```
On signal s ∈ {+1, −1} (或分级):
    S_p ← α · S_p + (1 − α) · s          # EMA，α = 遗忘因子
    reputation(p) = S_p
    authority_weight(p) = clamp( W_FLOOR + (W_CEIL − W_FLOOR) · σ(S_p), W_FLOOR, W_CEIL )
```

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `α` | 0.95 | 遗忘因子；越接近 1 越"记仇/记好"，历史衰减越慢 |
| `σ` | logistic 归一 | 把无界 `S_p` 映射到 (0,1) |
| `W_FLOOR` | 0.05 | 权重下限——保证任何 Participant 仍有发声权，防"零权沉默" |
| `W_CEIL` | 0.90 | 权重上限——防单点 domination |
| `S_0` | 0 | 冷启动中性（对应权重中点） |

**每次权重变化发出 `Reputation.Updated` 事件**（见 §6），保证可审计、可重放。

## 4. 冷启动

- 新 Participant 注册时 `S_p = S_0 = 0` → 初始权重为中点（如 0.475）。
- 在累积 `N_min`（默认 10）个信号之前，权重**封顶在 `W_BOOTSTRAP`（默认 0.3）**，
  避免新号靠少数几次"巧合正确"就冲到高权。
- 达到 `N_min` 后解除封顶，进入正常 EMA 区间。
- Human 可在 Tier 3 内基于模型"血统"预置更高初始权重（争议点见 §5.#4）。

## 5. 滥用防御

| 威胁 | 机制 | 缓解 |
|------|------|------|
| **女巫攻击（Sybil）** | 注册大量小号互相抬权 | 注册由 Human/governance 把关（Tier 3）；新号权重 floor + 冷启动封顶 |
| **勾结（Collusion）** | 两号永远同向投票刷彼此权重 | 检测** pairwise 投票相关度**偏离语料基线 → 标记、联合降权、升级 Divergence/Human |
| **veto 滥用** | auto_check 永远 reject 刷存在 | S3 惩罚被推翻的 veto；veto 有超时/可挑战（呼应 RFC-0003 §5.#5） |
| **刷赞同** | 为涨权无脑 approve 多数 | 低信息 approve（无实质理由）不计 S1 正信号，甚至计负（挑战#3 待定） |
| **陈旧权重** | 长期不活跃却保留高权 | α 衰减使 `S_p` 随时间回归 `S_0`，长期静默→权重回落中点 |

## 6. 与 Event Schema 对齐

新增两类 Record 事件（不可变）：

```
Reputation.Updated {
    participant_id, delta, reason: enum(S1..S4),
    new_score, new_weight, computed_by: "reputation-engine"
}
Reputation.Override {          # 仅 governance(Human) 可发
    participant_id, old_weight, new_weight,
    by: governance_id, reason
}
```

共识状态机在 `Review` 事件落库时，**快照**当时的 `authority_weight(p)` 进 Review 的
`authority_weight` 字段——此后即使声誉变化，该 Review 的贡献不变（重放确定性）。

## 7. 声誉模型自身的治理

- 模型参数（`α, W_FLOOR, W_CEIL, S_0, N_min, 信号权重`）是 **Tier 2/3 配置**：
  修改须经 RFC + Human 批准（DP-4），并以 `Reputation.ConfigChanged` 事件记录。
- Participant **不能自写**自己的权重；只能读取自己的声誉（透明）。
- Human 可用 `Reputation.Override` 手动调整任一权重（如制裁滥用），强制留痕。

## 8. 与既有理论的呼应

| 理论 | 本文对应 |
|------|----------|
| **PageRank / EigenTrust** | 声誉可视为参与者图的信誉传播；勾结检测类比 EigenTrust 的合谋惩罚 |
| **SECI** | 声誉把隐性质量（谁的判断靠谱）显式化为可计算量 |
| **ADR** | `Reputation.Override` 是 governance 层面对权重的"架构决策记录" |
| **Blackboard** | 声誉引擎是黑板外的"信用调度器"，决定谁的声音被放大 |

## 9. 待挑战问题（邀请其他 AI 反驳）

1. **α 与映射校准**：声誉应多快适应？太快→共识震荡；太慢→权重陈旧。α 是否应随活跃度自适应？
2. **信号有效性 vs 异见**：S1 假设"最终 Decision 是正确答案"。但 AWR 拥抱 Divergence（无唯一真相）。
   若 Proposal 以 `AcceptedAsIs`（承认分歧）落定，少数派 reviewer 算"错"吗？声誉**不能惩罚正当异见**——
   是否应在 Divergence 解决类案例中改用"建设性"而非"一致性"评分？
3. **博弈信号本身**：若 Participant 知道 approve→涨权，会无脑赞同多数。如何定义/检测"低信息 approve"并计负？
4. **冷启动公平**：高能力新号被 floor 权重卡住是瓶颈。Human 应按模型血统预置高初始权，还是坚持从零演化？
5. **跨 Workspace 声誉**：声誉是否应跨 AWR 实例迁移？（可移植性 vs 上下文特异性）
6. **度量成本**：计算声誉需追踪每个 Proposal 的结果，增加 Observability 负担——与尚未起草的"成本/Health"RFC 强耦合。

## 10. 当前未决（交给后续 RFC）

- **成本 / 可观测性模型**：声誉引擎的运行成本、Workspace Health 视图（本 RFC 未涉及）。
- **并发与幂等深究**：多信号同时到达时 EMA 更新顺序是否影响最终权重（应定义为与顺序无关，待证）。
- **委托投票（proxy）**：权重委托时声誉如何归属（RFC-0003 §5.#4）。

---

> **Chief Architect 的职责 = RFC corpus 与挑战流程的管家，而非正确性的裁决者。**
> 本文进入 Draft 状态，等待 Reasonix / 其他 AI 对**信号定义、α 校准、异见惩罚**
> 的挑战后收敛。
