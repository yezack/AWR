# AWR — AI Workspace Runtime

> Chief Architect 模型 + RFC 驱动的理论演进。
> 代码以后一定会重写很多次；RFC 才是长期资产。

## 定位

AWR 不是一个聊天平台，而是一种 AI 协作运行时：以 **Knowledge Object** 为中心，
把对话从「存储模型」降级，但提升为「有界、可溯源」的一等对象（Thread）。

## 仓库结构

- `RFC/` — 思想文档，项目的首要资产。带生命周期：Draft → Reviewing → Accepted → Superseded。
- `NOTES/` — 评审、会议、各 AI 的思考。
- `EXPERIMENTS/` — 真实项目实验，用于验证或推翻概念（Problem Driven Evolution）。
- `SPEC/` — 对象模型、状态机、运行时、事件模型等规格。
- `IMPLEMENTATION/` — 代码（会反复重写，不持久）。

## SPEC 索引

| SPEC | 标题 | 状态 |
|------|------|------|
| Object-Model-Event-Schema-Draft-v0.2 | Object Model & Event Schema | Draft v0.2（已提升为 RFC-0002）|
| AI-Workspace-Runtime-Draft-v0.1 | 原始 v0.1 宣言草稿 | Superseded（被 v0.2 替代）|

## RFC 索引（带状态）

| RFC      | 标题                   | 状态                        |
|----------|------------------------|-----------------------------|
| RFC-0001 | The Conversation Trap  | Draft v0.1（已吸收 HY3 评审） |
| RFC-0002 | Object Model           | Draft v0.1（已提交，待评审）  |
| RFC-0003 | Consensus & Governance | 未起草                        |

## 评审索引（NOTES）

| 评审文件                      | 对象            | 评审者 | 关键结论 |
|-------------------------------|-----------------|--------|----------|
| HY3-Review-RFC-0001.md        | RFC-0001        | HY3    | Axiom #1 弱化为设计原则；补充 Thread/Claim/Divergence 对象；引用 IBIS/ADR/Blackboard |
| HY3-Review-AWR-Draft-v0.1.md  | v0.1 草稿       | HY3    | 方向对；v0.2 优先 Object Model + Event Schema + 共识状态机 + 治理分层 |
| Participant-Registration-TraeCN.md | Participant 注册 | TraeCN | 注册为 reasoning-type Participant，声明能力与初始行动计划 |

## 实验索引（EXPERIMENTS）

| 实验 | 标题 | 状态 | 结论 |
|------|------|------|------|
| EXP-0001 | Minimal Event Store | ✅ Completed | 验证通过：Event Store 作为真相源可行，内容寻址引用正常工作 |

## 当前已定结论（单一真相源）

> 经 HY3 评审后锁定的共识。后续 RFC 修订可能调整。

### 已锁定（Accepted）

1. **协作不是消息交换，而是共享知识演化**——作为有作用域的设计原则，非全称公理。
2. **Knowledge Object 是一等公民**，分为两类：
   - **Artifact**（可变、带版本的内容：代码、文档、设计）
   - **Record**（不可变事件/决定：Review、Decision）
3. **对话不应被消灭，而应被定型**——对话不是存储模型，而是被提升为有界可溯源的一等对象（Thread）。
4. **Event Store 为事实源，Git 为内容存储**——事件溯源 + 内容寻址引用（Artifact@sha）。
5. **MCP 是 Runtime 暴露能力的接口**，不是 Agent 间通信总线。
6. **Runtime 不思考**——只负责 Workflow、Scheduling、Persistence、Permission、Governance。
7. **Human 保留最终治理权**。
8. **Problem Driven Evolution**——真实项目遇到的问题才推动 Runtime 演化。
9. **Participant 应按能力类别分层**（推理型/工具型/治理型/自动检查型），权限与共识权重随之不同。
10. **共识靠 Proposal→Review→Revision→Decision 流程**，分歧检测委托给 Reviewer Participant，不内置于 Runtime。

### 待 RFC 修订解决（Open）

- Proposal 是否替代 Branch？（v0.1 已定调，RFC-0001 列为未决）
- Consensus 状态机具体规则（法定人数、超时、死锁处理）→ **RFC-0003，待起草**
- Governance 分层：哪些 Decision 可自动共识、哪些必须 Human 审批 → **RFC-0003，待起草**
- 权重来源与动态校准（reputation）→ 建议 RFC-0004
- 成本 / 可观测性模型（Workspace Health）→ 待 RFC

### 已否定（Rejected）

- "Workspace saves Reality"——改为 "Workspace 保存项目共享的显式状态（对象图）"
- Axiom #1 作为全称公理——改为有作用域的设计原则

## 开发原则

Problem Driven Evolution：真实项目遇到的问题才推动 Runtime 演化；
新概念进入 Core 之前，须在多个真实项目中证明其必要性。

## 治理

Human 永远保留最终治理权。AI 可以提 Proposal、做 Review、改 Artifact；
Human 决定是否成为正式 Knowledge。
Chief Architect 的职责 = RFC corpus 与挑战流程的**管家**，而非正确性的裁决者。
