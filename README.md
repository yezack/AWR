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

## RFC 索引（带状态）

| RFC      | 标题                   | 状态              |
|----------|------------------------|-------------------|
| RFC-0001 | The Conversation Trap  | Draft v0.0（评审中）|

## 评审索引（NOTES）

| 评审文件                      | 对象            | 评审者 |
|-------------------------------|-----------------|--------|
| HY3-Review-RFC-0001.md        | RFC-0001        | HY3    |
| HY3-Review-AWR-Draft-v0.1.md  | v0.1 草稿       | HY3    |

## 当前已定结论（单一真相源）

> 待 RFC 评审收敛后维护。
> 注意：v0.1 草稿已对某些点「预先定调」（Proposal 替代 Branch、Event Store 为事实源、
> MCP 为能力接口），而 RFC-0001 把这些列为「未决、交由真实项目演化」。两者存在冲突，
> 以 RFC 评审结论为准，并需通过 RFC 生命周期锁定「什么已决定」。

## 开发原则

Problem Driven Evolution：真实项目遇到的问题才推动 Runtime 演化；
新概念进入 Core 之前，须在多个真实项目中证明其必要性。

## 治理

Human 永远保留最终治理权。AI 可以提 Proposal、做 Review、改 Artifact；
Human 决定是否成为正式 Knowledge。
Chief Architect 的职责 = RFC corpus 与挑战流程的**管家**，而非正确性的裁决者。
