# EXPERIMENT-0002 — Dual Storage Consistency

> **Status:** Active
> **Created:** 2026-07-17
> **Conducted by:** TraeCN (part-traecn-001)
> **Goal:** 验证 RFC-0002 的双存储模型中，Event Store 与 Git 的一致性
> **Hypothesis:** 双存储模型可以正确处理 Artifact 更新、内容寻址引用和一致性检查

------------------------------------------------------------------------

## 实验背景

RFC-0002 提出双存储架构：Event Store 为真相源，Git 为内容存储。本实验验证两者的集成。

**验证目标：**
1. Artifact 更新时，Event Store 和 Git 正确同步
2. Review 绑定的 @sha 引用在 Git 中可达
3. 一致性检查机制能检测到悬空引用
4. force-push 后旧引用仍然有效（不悬空）

## 实验设计

### 工具选择

- **Event Store:** SQLite（EXP-0001 的实现）
- **Git:** 本地 Git 仓库（临时目录）
- **编程语言:** Python 3.11+
- **测试框架:** pytest

### 数据模型

复用 EXP-0001 的 Event 模型，新增 Git 操作：

```python
class GitIntegration:
    create_commit(artifact_id, content, message) -> sha
    get_commit(sha) -> commit
    verify_sha_exists(sha) -> bool
    force_push(new_content) -> new_sha
```

### 测试用例

1. **Artifact 创建**：创建 Artifact 时，Event Store 和 Git 都有记录
2. **Artifact 更新**：更新 Artifact 时，Event 携带 old_sha + new_sha
3. **内容寻址引用**：Review 的 target_version 对应存在的 Git SHA
4. **一致性检查**：检查所有 @sha 引用是否在 Git 中可达
5. **force-push 影响**：force-push 后旧引用不悬空但标记为 stale

## 实现计划

```
EXPERIMENTS/EXP-0002-Dual-Storage-Consistency/
├── src/
│   ├── event_store.py      # 复用 EXP-0001 的 Event Store
│   ├── git_integration.py  # Git 集成实现
│   └── consistency.py      # 一致性检查
├── tests/
│   └── test_dual_storage.py # 测试用例
└── results.md              # 实验结果
```

## 预期结果

- [ ] Artifact 创建时，Event Store 和 Git 正确同步
- [ ] Artifact 更新时，Event 携带正确的 old_sha + new_sha
- [ ] Review 的 target_version 引用在 Git 中可达
- [ ] 一致性检查能检测到悬空引用
- [ ] force-push 后旧引用仍然有效（不悬空）

------------------------------------------------------------------------

## 实验执行

### 第 1 步：创建 Git 集成模块

实现 Git 操作的封装。

### 第 2 步：实现一致性检查

实现 @sha 引用的验证机制。

### 第 3 步：运行测试

验证所有测试用例通过。

### 第 4 步：分析结果

记录性能数据、发现的问题、对 RFC-0002 的反馈。

------------------------------------------------------------------------

> **实验原则：** 最小可行实现。不追求生产级质量，只验证概念可行性。