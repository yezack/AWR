# EXPERIMENT-0002 — Minimal Dual Storage (Event Store + Git)

> **Status:** Active
> **Created:** 2026-07-17
> **Conducted by:** Reasonix (part-reasonix-001)
> **Goal:** 验证 RFC-0002 双存储模型：Event Store 为真相源 + Git 为内容存储
> **Hypothesis:** Event Store 与 Git 可以通过内容寻址引用（@sha）保持一致性，force-push 不破坏 Event Store 中的引用

------------------------------------------------------------------------

## 实验背景

EXP-0001 验证了 Event Store 可以独立工作。本实验验证第二个关键组件——Event Store 与 Git 的双存储一致性模型，这是 RFC-0002 的核心设计。

**验证目标：**
1. Artifact 创建 → Event 写入 `Artifact.Created` → Git 有对应 commit
2. Artifact 更新 → Event 写入 `Artifact.Updated`（带 old_sha/new_sha）
3. Review 绑定 `Artifact@sha`，Git force-push 后引用不悬空
4. Materialized View 从 Event 重建对象图状态
5. 一致性规则检查（event 发出前 commit 存在、@sha 引用可达）

## 实验设计

### 架构

```
DualStore
├── EventStore (SQLite, 复用 EXP-0001)
│   ├── write_event()
│   ├── get_events_by_type()
│   └── materialize_object()
├── GitStore (GitPython / subprocess)
│   ├── init_repo()
│   ├── write_artifact(path, content) → sha
│   ├── read_artifact(sha) → content
│   └── artifact_exists(sha) → bool
├── ConsistencyChecker
│   ├── check_artifact_created_has_commit()
│   ├── check_review_target_exists()
│   └── check_all_references_reachable()
└── MaterializedView
    └── rebuild_object_graph() → dict[id, object_state]
```

### 测试用例

1. **创建流程**：创建 Artifact（Git）→ 写 Event（Event Store）→ 验证双写一致性
2. **更新流程**：更新 Artifact → 写 Event（带 old_sha/new_sha）→ 验证引用链
3. **Review 绑定**：Review 绑定 Artifact@sha → force-push 新内容 → 旧 Review 仍指向旧 sha
4. **对象图重建**：从 Event Store 的所有事件重建完整的对象图状态
5. **一致性检查**：所有 Event 引用的 @sha 在 Git 中可达

### 工具选择

- **Event Store:** SQLite（复用 EXP-0001）
- **Git:** subprocess（`git` CLI），避免 GitPython 依赖
- **编程语言:** Python 3.11+
- **测试框架:** pytest

## 预期结果

- [ ] Artifact 创建事件与 Git commit 一一对应
- [ ] Artifact 更新事件的 old_sha/new_sha 与 Git history 一致
- [ ] force-push 后旧 Review 仍可追溯（@sha 不悬空）
- [ ] Materialized View 可以重建对象图状态
- [ ] 一致性检查通过

## 风险与边界

- **Git subprocess 跨平台**：Windows 路径处理需注意
- **force-push 模拟**：实验用独立 bare repo 或 `git commit --amend` 模拟
- **性能**：不测量大规模数据下的性能

## 实现计划

```
EXPERIMENTS/EXP-0002-Minimal-Dual-Storage/
├── src/
│   ├── event_store.py      # 复用 EXP-0001（软链或复制）
│   ├── git_store.py        # Git 操作封装
│   ├── dual_store.py       # 双存储一致性层
│   └── models.py           # 数据模型（复制 EXP-0001）
├── tests/
│   └── test_dual_store.py  # 测试用例
├── run_experiment.py       # 实验入口
└── results.md              # 实验结果
```

------------------------------------------------------------------------

> **实验原则：** 最小可行实现。验证双存储一致性模型的核心逻辑，不追求生产级质量。
