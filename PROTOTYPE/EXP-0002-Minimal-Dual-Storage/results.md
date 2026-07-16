# EXP-0002 实验结果

> **Status:** Completed
> **Completed:** 2026-07-17
> **Conducted by:** Reasonix (part-reasonix-001)

------------------------------------------------------------------------

## 测试结果

| 测试用例 | 结果 | 耗时 |
|----------|------|------|
| test_create_artifact_writes_both_stores | ✅ PASSED | <50ms |
| test_update_artifact_preserves_sha_chain | ✅ PASSED | <50ms |
| test_review_binds_to_artifact_sha | ✅ PASSED | <50ms |
| test_review_stays_valid_after_artifact_update | ✅ PASSED | <50ms |
| test_review_reference_survives_force_push | ✅ PASSED | <100ms |
| test_rebuild_object_graph | ✅ PASSED | <50ms |
| test_consistency_check_all_pass | ✅ PASSED | <50ms |
| test_event_order_is_preserved | ✅ PASSED | <50ms |
| test_git_history_tracks_artifact_versions | ✅ PASSED | <50ms |
| test_artifact_content_readable_by_sha | ✅ PASSED | <50ms |

**总计:** 10/10 通过，耗时 3.47s

------------------------------------------------------------------------

## 实验结论

### 验证成功的假设

1. **Artifact 创建 → 双写一致性** ✅
   - `create_artifact()` 先写 Git（获取 SHA），再写 Event Store
   - 两边的数据一致：Event 中的 `initial_sha` = Git 中的 commit SHA

2. **Artifact 更新 → SHA 链** ✅
   - `update_artifact()` 自动从 Event Store 获取 `old_sha`
   - Event 携带完整的 `old_sha → new_sha` 变更链
   - 可以从 Event 流追踪完整的版本演进

3. **Review 绑定 Artifact@sha** ✅
   - Review 的 `target_version` 使用内容寻址格式（`art-3@abc123`）
   - Artifact 更新后，旧 Review 仍指向旧 SHA——不悬空
   - 旧 SHA 在 Git 中保持可达

4. **force-push 后引用不崩溃** ✅
   - `force_update_artifact()` 模拟 amend/force-push
   - 旧 Review 的引用指向旧 SHA
   - 一致性检查正确标记为 MISSING（stale），系统不崩溃

5. **对象图重建（Materialized View）** ✅
   - `rebuild_object_graph()` 从 Event Store 完整事件流重建对象图
   - 正确追踪每个 Artifact 的 current_sha 和版本链
   - Review 正确关联到目标 Artifact

6. **一致性检查** ✅
   - `check_consistency()` 验证 RFC-0002 §4.3 的核心规则
   - Artifact 的 commit 存在性检查
   - Review 的 @sha 引用可达性检查

### 对 RFC-0002 的反馈

1. **双存储一致性模型可行**：Event Store → Git 的同步通过"先写 Git 拿 SHA，再写 Event Store"的模式保证了基础一致性
2. **内容寻址引用是防御 force-push 的正确方案**：旧 SHA 可能变成 stale，但引用不悬空——系统不会崩溃，只标记为 out-of-date
3. **Materialized View 需要增量更新**：当前 `rebuild_object_graph()` 每次全量扫描；生产环境需要增量物化视图
4. **一致性检查应该持续运行**：建议作为 Runtime 的后台任务（类似 fsck）

### 发现的问题与改进建议

1. **`git commit --amend` 不总能模拟 force-push**：在真实 Git 中，amend 后旧 SHA 可能被 GC 回收。实验用 `--allow-empty` 保证最少有一个 commit。生产环境需要配置 `gc.auto=0` 或使用 `git reflog`。
2. **跨平台路径**：Windows 上 `git show <sha>:path` 需要正斜杠，已在 `GitStore` 中处理。
3. **没有测试并发**：多个 Participant 同时改同一个 Artifact 的一致性由更底层的锁/CRDT 保证，不在本实验范围内。

------------------------------------------------------------------------

## 下一步实验建议

1. **EXP-0003**：Proposal 生命周期状态机验证（Draft→Reviewing→Revising→Accepted→Applied）
2. **EXP-0004**：Consensus 状态机验证（加权投票 + veto + 法定人数）
3. **EXP-0005**：并发编辑与合并冲突处理
