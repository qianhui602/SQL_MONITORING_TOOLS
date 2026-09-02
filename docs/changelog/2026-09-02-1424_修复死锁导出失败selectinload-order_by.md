# 变更记录 - 修复死锁导出失败(selectinload.order_by)

- **日期**: 2026-09-02 14:24
- **类型**: Bug修复
- **影响范围**: `backend/app/routers/export.py`

## 变更内容
死锁监控导出在上一轮新增「关联SQL语句」列后提示「导出失败，请重试」。根因是使用了 `selectinload(DeadlockEvent.deadlock_sqls).order_by(DeadlockSql.session_id)`：SQLAlchemy 2.0 中 `selectinload()` 返回的 loader 对象不支持 `order_by` 子句，请求执行时抛出 `AttributeError: 'Load' object has no attribute 'order_by'`，后端返回 500，前端捕获异常提示导出失败。

修复：
1. 移除 `selectinload(...).order_by(...)`，仅保留 `selectinload(DeadlockEvent.deadlock_sqls)`；
2. 改为在 `row_generator` 聚合循环内用 `sorted(key=lambda s: (s.session_id is not None, s.session_id))` 对每个事件的 SQL 明细排序；
3. 清理不再使用的 `DeadlockSql` 导入。

已用内存 SQLite + SQLAlchemy 2.0.52 真实执行 selectinload 查询与聚合逻辑验证通过。

## 变更原因
上一轮提交的 `selectinload().order_by()` 语法在 SQLAlchemy 2.0 中不存在，导致死锁导出接口 500 错误。

## 涉及文件
| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| `backend/app/routers/export.py` | 修改 | 移除 selectinload.order_by，改为 Python 侧排序；移除未使用的 DeadlockSql 导入 |