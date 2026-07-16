# EXP-0002 实验结果

> **Status:** Completed
> **Completed:** 2026-07-17
> **Conducted by:** TraeCN (part-traecn-001)

------------------------------------------------------------------------

## 测试结果

| 测试用例 | 结果 | 耗时 |
|----------|------|------|
| test_artifact_creation_sync | ✅ PASSED | ~1s |
| test_artifact_update_with_sha_pair | ✅ PASSED | ~1s |
| test_review_target_version_reference | ✅ PASSED | ~1s |
| test_consistency_checker_detects_dangling_reference | ✅ PASSED | <1ms |
| test_force_push_does_not_break_old_references | ✅ PASSED | ~1s |
| test_artifact_consistency_check | ✅ PASSED | ~1s |
| test_cross_reference_validation | ✅ PASSED | ~1s |

**总计:** 7/7 通过，耗时 59.22s

------------------------------------------------------------------------

## 实验结论

### 验证成功的假设

1. **Artifact 创建同步** ✅
   - Event Store 和 Git 正确同步
   - Artifact.Created 事件携带 initial_sha

2. **Artifact 更新同步** ✅
   - Artifact.Updated 事件携带 old_sha + new_sha
   - 两个 SHA 都在 Git 中可达

3. **内容寻址引用** ✅
   - Review 的 target_version 格式（如 `art-3@abc123`）可以正确解析
   - 一致性检查器能验证引用的有效性

4. **悬空引用检测** ✅
   - 一致性检查器能检测到不存在的 SHA 引用
   - 返回明确的错误信息

5. **force-push 影响** ✅
   - force-push 后旧 SHA 仍然在 Git 中可达
   - 旧 Review 引用不悬空，但可能指向过时版本

6. **跨引用验证** ✅
   - Decision 引用 Proposal 的 @sha 格式正确工作

### 发现的问题与改进建议

1. **GitPython API 差异**
   - 不同版本的 GitPython API 略有差异
   - 建议在生产环境中封装更稳定的 Git 操作接口

2. **Blob SHA vs Commit SHA**
   - 当前实现使用 Commit SHA，而非 Blob SHA
   - 生产环境应区分：Commit SHA 用于版本引用，Blob SHA 用于内容引用

3. **性能考虑**
   - 测试环境中每次操作耗时约 1s（Git 操作开销）
   - 生产环境需要批量操作和缓存优化

### 对 RFC-0002 的反馈

1. **双存储模型可行**：Event Store + Git 的集成在实现层面没有问题
2. **内容寻址引用可行**：`artifact_id@sha` 格式可以正确解析和验证
3. **一致性检查可行**：可以检测悬空引用和不一致状态
4. **需要补充 Blob SHA 规范**：RFC-0002 没有明确区分 Commit SHA 和 Blob SHA

------------------------------------------------------------------------

## 下一步实验建议

1. **EXP-0003**：Proposal 生命周期状态机验证
2. **EXP-0004**：共识状态机验证（基于 RFC-0003）
3. **EXP-0005**：完整的 AWR 工作流端到端测试