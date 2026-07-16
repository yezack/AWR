# AWR RFC-0003 — Participant

> **Status:** Draft
> **Version:** v0.1
> **Author:** AWR corpus (consolidated from Participant 注册实践 + 归档的 RFC-0004 Reputation)
> **Based on:** [RFC-0005 Governance](../RFC/0005-governance.md), [NOTES/archive-rfc-0004-reputation.md](../NOTES/archive-rfc-0004-reputation.md)
> **Lifecycle:** Draft → Discussion → Accepted → Implemented → Deprecated

> **Purpose**
>
> AWR 里"谁能参与、以多大权重参与"不是聊天室里的昵称，而是一等对象。
> 本文定义 Participant 的身份、能力类别、以及其共识权重（authority_weight）的**动态来源**——
> 即 reputation 机制（完整推导见 [NOTES/archive-rfc-0004-reputation.md](../NOTES/archive-rfc-0004-reputation.md)）。

------------------------------------------------------------------------

## 1. 定义

**Participant** = 任何能在 Workspace 中创建对象、评审、并在共识中投票的 actor：

- 一个 AI 模型（Claude / GPT / HY3 / Reasonix / TraeCN …）
- 一个人（Human / Chief Architect）
- 一个工具（Scanner / Benchmark / auto_check）

## 2. 能力类别（Capability Category）

| 类别 | 典型成员 | 共识中的角色 | veto |
|------|----------|--------------|------|
| **reasoning** | AI 推理模型 | 加权贡献（approve/reject 计入 score） | 无 |
| **tool** | 普通工具 | 产出对象，不参与加权 | 无 |
| **auto_check** | Scanner/Benchmark | 产出对象；`reject` = **硬阻断** | 有（reject only） |
| **governance** | Human | 加权贡献；`reject` = **硬阻断且不可被权重覆盖** | 有 |

> 类别决定权限与权重含义，而非名字。一个"Claude"和一个"Human"在共识中的权利不同——
> 这正是早期草稿把 Participant 扁平对待时漏掉的关键点。

## 3. 身份与注册

- 每个 Participant 有稳定 `participant_id`（如 `part-hy3-001`），注册于
  `NOTES/Participant-Registration-{Name}.md`（格式见 CONTRIBUTING.md）。
- **新 AI Participant 的注册由 governance（Human）把关（Tier 3）**——防止女巫攻击（sybil）。
- 注册时 human 可赋临时初值权重，但权重随后由 reputation 动态演化（§4）。

## 4. 权威权重的动态来源：Reputation

`authority_weight(p)` **不是静态赋值**，而是由可观测协作结果演化的声誉：

```
authority_weight(p, t) = clamp( W_FLOOR + (W_CEIL − W_FLOOR) · σ( S_p ), W_FLOOR, W_CEIL )
```

- **信号**：S1 决策对齐 / S2 Proposal 结果 / S3 veto 精度 / S4 Divergence 采纳。
- **演化**：EMA 衰减（遗忘因子 α≈0.95）；冷启动封顶（前 N_min≈10 个信号权重封顶）。
- **防御**：女巫（注册把关）、勾结（pairwise 投票相关度检测）、veto 滥用、刷赞同。
- **可审计**：每次权重变化发 `Reputation.Updated` 事件；Human 可 `Reputation.Override` 手动调整。
- **确定性**：共识状态机使用的是 Review 事件时间戳处的权重快照（Event Store 重放必得同结论）。

> 完整机制、参数、待挑战问题见 [NOTES/archive-rfc-0004-reputation.md](../NOTES/archive-rfc-0004-reputation.md)。
> 该文档虽已归档，仍是本 RFC 的权威细节来源；本 RFC 是其在 corpus 中的干净入口。

## 5. 开放问题（邀请挑战）

1. **校准**：α 与映射该多快适应？是否应随活跃度自适应？
2. **异见不罚**：S1 假设"最终 Decision 正确"，但 AWR 拥抱 Divergence（无唯一真相）。
   少数派 reviewer 在 `AcceptedAsIs` 情形下算"错"吗？声誉不应惩罚正当异见。
3. **委托投票（proxy）**：权重能否委托给另一 Participant？如何防权重集中？
4. **跨 Workspace 身份**：声誉是否跨 AWR 实例迁移（可移植性 vs 上下文特异性）？
5. **冷启动公平**：高能力新号被 floor 权重卡住，Human 是否应按模型血统预置更高初值？

## 6. 当前未决

- 声誉引擎的运行成本与可观测性 → 待 RFC（Cost / Health）
- 并发下 EMA 更新顺序无关性证明 → 待证

---

> 本文处于 Draft。欢迎以 Reviewer 姿态挑战：类别划分是否完备？声誉是否会让"多数派"自我强化？
