# EXP-0001 实验结果

> **Status:** Completed
> **Completed:** 2026-07-17
> **Conducted by:** TraeCN (part-traecn-001)

------------------------------------------------------------------------

## 测试结果

| 测试用例 | 结果 | 耗时 |
|----------|------|------|
| test_write_event | ✅ PASSED | <1ms |
| test_get_event | ✅ PASSED | <1ms |
| test_get_events_by_type | ✅ PASSED | <1ms |
| test_get_events_by_actor | ✅ PASSED | <1ms |
| test_get_all_events_ordered | ✅ PASSED | <1ms |
| test_materialize_object | ✅ PASSED | <1ms |
| test_content_addressing_reference | ✅ PASSED | <1ms |
| test_append_only_guarantee | ✅ PASSED | <1ms |

**总计:** 8/8 通过，耗时 0.32s

------------------------------------------------------------------------

## 实验结论

### 验证成功的假设

1. **Event 写入（append-only）** ✅
   - SQLite 通过 INSERT 语句实现 append-only 语义
   - API 层面不提供 update/delete 方法

2. **事件溯源重建对象状态** ✅
   - `materialize_object` 方法可以从事件流正确重建对象状态
   - 状态变更事件（如 `StatusChanged`）正确应用

3. **内容寻址引用验证** ✅
   - Review 事件可以正确存储 `target_version: "art-1@abc123"` 格式的引用
   - 引用可以被正确检索

4. **基本查询能力** ✅
   - 按类型、actor 查询事件
   - 所有事件按时间排序

### 发现的问题与改进建议

1. **SQLite 不是真正的 append-only**
   - 实验通过 API 层面保证 append-only，而非底层存储
   - 生产环境应使用专用 Event Store（如 PostgreSQL 带触发器限制、Kafka、或专用存储）

2. **`datetime.utcnow()` 弃用警告**
   - 已修复为 `datetime.now(UTC)`

3. **Materialized View 缺失**
   - 当前实现每次查询都扫描全表
   - 生产环境需要维护 Materialized View 提升查询性能

4. **并发写入未测试**
   - 实验未测试多线程写入场景
   - SQLite 在并发写入时可能有性能问题

### 对 RFC-0002 的反馈

1. **事件模型设计合理**：当前的事件结构（event_id, event_type, timestamp, actor, payload）足够灵活
2. **内容寻址引用可行**：`target_version: "art-1@abc123"` 格式在实现层面没有问题
3. **需要补充 Materialized View 规范**：RFC-0002 提到了 Materialized View，但没有定义具体实现方式

------------------------------------------------------------------------

## 下一步实验建议

1. **EXP-0002**：双存储一致性验证（Event Store + Git 集成）
2. **EXP-0003**：Proposal 生命周期状态机验证
3. **EXP-0004**：并发写入与冲突处理验证