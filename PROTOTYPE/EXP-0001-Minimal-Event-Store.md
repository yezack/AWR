# EXPERIMENT-0001 — Minimal Event Store

> **Status:** Active
> **Created:** 2026-07-17
> **Conducted by:** Reasonix (part-reasonix-001)
> **Goal:** 验证 RFC-0002 的双存储模型中，Event Store 作为真相源的可行性
> **Hypothesis:** 用 SQLite 实现的最小 Event Store 可以支撑 AWR 的对象状态追踪

------------------------------------------------------------------------

## 实验背景

RFC-0002 提出双存储架构：Event Store 为真相源，Git 为内容存储。本实验验证第一个部分——用最小实现验证 Event Store 的核心能力。

**验证目标：**
1. Event 写入（append-only）
2. 事件溯源重建对象状态
3. 内容寻址引用验证
4. 基本查询能力

## 实验设计

### 工具选择

- **Event Store:** SQLite（文件存储，append-only 语义通过事务保证）
- **编程语言:** Python 3.11+
- **测试框架:** pytest

### 数据模型

```python
class Event:
    event_id: UUID
    event_type: str
    timestamp: datetime
    actor: str
    payload: dict
```

### 测试用例

1. **写入测试**: 连续写入多个事件，验证顺序性
2. **溯源测试**: 从事件流重建对象状态
3. **引用测试**: 创建带 @sha 引用的事件，验证引用完整性
4. **查询测试**: 按类型、actor、时间范围查询事件

## 实现计划

```
PROTOTYPE/EXP-0001-Minimal-Event-Store/
├── src/
│   ├── event_store.py      # Event Store 核心实现
│   └── models.py           # 数据模型
├── tests/
│   └── test_event_store.py # 测试用例
├── run_experiment.py       # 实验入口
└── results.md              # 实验结果
```

## 预期结果

- [ ] Event Store 可以正确写入事件（append-only）
- [ ] 可以从事件流重建对象状态
- [ ] 内容寻址引用可以被正确存储和检索
- [ ] 查询性能满足最小需求（<100ms 响应）

## 风险与边界

- **SQLite 限制**: 不支持真正的 append-only（可以 delete/update）
- **并发写入**: 未考虑多线程写入场景
- **性能**: SQLite 在大规模数据下性能有限

这些限制是实验性的——真实实现会选择专用的 Event Store（如 Kafka、PostgreSQL with append-only tables）。

------------------------------------------------------------------------

## 实验执行

### 第 1 步：初始化环境

创建 Python 项目结构和依赖。

### 第 2 步：实现 Event Store

实现核心写入、读取、查询能力。

### 第 3 步：运行测试

验证所有测试用例通过。

### 第 4 步：分析结果

记录性能数据、发现的问题、对 RFC-0002 的反馈。

------------------------------------------------------------------------

> **实验原则：** 最小可行实现。不追求生产级质量，只验证概念可行性。