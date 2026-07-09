# 增加 SQL 断联监控功能

## 概述

在现有 SQL 监控平台中增加数据库连接断开检测与告警功能，在每次采集周期中主动检测 SQL Server 连接是否存活，当连接断开或恢复时自动产生告警通知，并在实例管理页面展示连接状态。

---

## 一、准备工作

### 1.1 拉取最新 Git 代码
```bash
git pull origin main
```

---

## 二、后端修改（共 5 个文件）

### 2.1 实体模型扩展 — `backend/app/models/instance.py`

**目标**：在 `MonitoredInstance` 表中增加连接状态跟踪字段

**变更**：
- 添加 `is_connected: bool` — 当前是否已连接（默认 True）
- 添加 `last_connected_at: datetime` — 最后成功连接时间（可空）
- 添加 `last_disconnected_at: datetime` — 最后断开时间（可空）
- 添加 `connection_error: str` — 最近的连接错误信息（可空）

```python
# 新增字段定义
is_connected: Mapped[bool] = mapped_column(
    Boolean, nullable=False, default=True,
    comment="当前连接状态：True=在线，False=离线",
)
last_connected_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=True, default=None,
    comment="最后成功连接时间",
)
last_disconnected_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=True, default=None,
    comment="最后断开时间",
)
connection_error: Mapped[str] = mapped_column(
    String(500), nullable=True, default=None,
    comment="最近的连接错误信息",
)
```

### 2.2 数据迁移 — `backend/app/init_db.py`

**目标**：在应用启动时自动为 `monitored_instances` 表补充新字段

**变更**：在 `_run_migrations()` 函数末尾添加新字段的迁移检查

```python
# 在 _run_migrations() 末尾添加：
# 为 monitored_instances 表添加连接状态字段
for col, typ, default in [
    ("is_connected", "BOOLEAN", "TRUE"),
    ("last_connected_at", "TIMESTAMPTZ", "NULL"),
    ("last_disconnected_at", "TIMESTAMPTZ", "NULL"),
    ("connection_error", "VARCHAR(500)", "NULL"),
]:
    result = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'monitored_instances' AND column_name = :col"
        ),
        {"col": col},
    )
    if not result.first():
        alter = f"ALTER TABLE monitored_instances ADD COLUMN {col} {typ}"
        if default != "NULL":
            alter += f" DEFAULT {default}"
        await conn.execute(text(alter))
        logger.info("迁移: monitored_instances 表添加 %s 列", col)
```

### 2.3 SQL Server 连接管理器 — `backend/app/collectors/sqlserver.py`

**目标**：添加轻量级快速连接检测方法 `ping()`

**变更**：在 `MSSQLConnectionManager` 类中新增 `ping()` 方法

```python
def ping(self) -> bool:
    """快速检测连接是否存活（轻量级 SELECT 1）

    Returns:
        bool: 连接正常返回 True，否则返回 False
    """
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True
    except (MSSQLConnectionError, pymssql.Error, Exception):
        return False
```

### 2.4 告警规则引擎 — `backend/app/services/alert_service.py`

**目标**：新增 2 条内置告警规则 `connection_lost` 和 `connection_recovered`

**核心设计**：
- 在 `metrics_data` 中新增 `connection_status` 对象，格式为：
  ```python
  {
      "server_address": "instance_name(host:port)",
      "is_connected": True/False,
      "connection_error": "错误信息或None",
      "previous_was_disconnected": True/False,  # 前次采集是否处于断开状态
  }
  ```
- 告警引擎通过此对象判断连接断开和恢复

**变更**：

1. 在 `AlertEngine.__init__` 中新增冷却期缓存（用于跨采集周期跟踪连接状态）：
   ```python
   # 跟踪每个实例的前次连接状态（server_address -> was_disconnected）
   self._last_connection_state: Dict[str, bool] = {}
   ```

2. 新增 2 个条件函数：
   ```python
   @staticmethod
   def _condition_connection_lost(metrics_data):
       """判断是否有实例连接断开"""
       for conn_status in metrics_data.get("connection_status", []):
           if not conn_status.get("is_connected", True):
               return True
       return False

   @staticmethod
   def _connection_recovered(metrics_data):
       """判断是否有实例连接恢复（前次断开，本次连接成功）"""
       for conn_status in metrics_data.get("connection_status", []):
           if conn_status.get("is_connected", True) and conn_status.get("previous_was_disconnected", False):
               return True
       return False
   ```

3. 在 `_builtin_rules` 中添加 2 条新规则：
   ```python
   AlertRule(
       alert_type="connection_lost",
       severity="critical",
       condition_func=self._condition_connection_lost,
       message_template=(
           "## SQL Server 连接断开\n\n"
           "- **实例**: {server_address}\n"
           "- **错误信息**: {error_message}\n"
           "- **最后连接时间**: {last_connected_at}\n"
           "- **触发时间**: {current_time}\n\n"
           "请立即检查 SQL Server 服务状态和网络连通性。"
       ),
       cooldown_minutes=10,
   ),
   AlertRule(
       alert_type="connection_recovered",
       severity="low",
       condition_func=self._connection_recovered,
       message_template=(
           "## SQL Server 连接已恢复\n\n"
           "- **实例**: {server_address}\n"
           "- **断开时长**: {down_duration}\n"
           "- **恢复时间**: {current_time}\n\n"
           "连接已恢复正常。"
       ),
       cooldown_minutes=5,
   ),
   ```

4. 修改 `check_rules()` 方法以处理新规则：
   - 在 `connection_lost` 分支中：提取断开的实例信息，格式化消息
   - 在 `connection_recovered` 分支中：提取恢复的实例信息，计算断开时长

### 2.5 定时采集调度器 — `backend/app/scheduler.py`

**目标**：在每次采集周期中增加连接预检，将连接状态传递给告警引擎

**核心逻辑**：
1. 在采集前调用 `MSSQLConnectionManager.ping()` 检测连接
2. 更新 `MonitoredInstance` 的 `is_connected` / `last_connected_at` 等字段
3. 将连接状态信息写入 `metrics_data["connection_status"]`
4. 连接失败时跳过该实例的指标采集，但仍执行告警检查
5. 在 `_run_alert_checks()` 中传递连接状态数据

**关键变更点**：

#### 修改 `_collect_multi_instance()` 方法：

```python
# 在每个实例采集开始时：
conn_mgr = MSSQLConnectionManager.get_connection_for_instance(...)

# 1. 连接预检
is_connected = conn_mgr.ping()
current_time = datetime.now(timezone.utc)

# 2. 查询前次连接状态
# 从已加载的 instance 对象获取上次状态

# 3. 更新实例的连接状态到数据库
async with async_session_factory() as session:
    instance.is_connected = is_connected
    if is_connected:
        instance.last_connected_at = current_time
        instance.connection_error = None
    else:
        instance.last_disconnected_at = current_time
        instance.connection_error = str(e) if e else "Connection timeout"
    session.add(instance)
    await session.commit()

# 4. 将连接状态写入 metrics_data
conn_status_item = {
    "server_address": server_address,
    "is_connected": is_connected,
    "connection_error": instance.connection_error,
    "previous_was_disconnected": not instance.is_connected,  # 前次状态
}

# 5. 如果连接成功，正常采集；否则跳过采集但继续
if is_connected:
    collector = MetricsCollector(connection_manager=conn_mgr)
    data = collector.collect_all_metrics()
    ...存储指标...
else:
    logger.warning("Instance %s is offline, skipping data collection", server_address)
```

#### 修改 `_collect_single_instance()` 方法：
- 类似的连接预检逻辑
- 连接失败时跳过采集

#### 修改 `_run_alert_checks()` 方法：
- 将 `connection_status` 合并到 `metrics_data` 中传递给告警引擎

#### 在 `SchedulerManager.__init__` 中新增：
```python
self._last_connection_cache: Dict[str, bool] = {}  # 实例连接状态缓存
```

### 2.6 实例 API — `backend/app/routers/instances.py`（小修改）

**目标**：实例列表 API 返回连接状态字段

**变更**：在 `InstanceResponse` 中添加新字段
```python
is_connected: bool = True
last_connected_at: Optional[datetime] = None
last_disconnected_at: Optional[datetime] = None
connection_error: Optional[str] = None
```

---

## 三、前端修改（共 2 个文件）

### 3.1 实例管理页 — `frontend/src/views/Instances.vue`

**目标**：在表格中显示实例的实时连接状态

**变更**：
1. "状态"列改为两种维度：
   - 第一维度：启用/禁用（灰色 ← 禁用）
   - 第二维度：在线/离线（绿色 ← 在线，红色 ← 离线）
   - 禁用态的实例不检测连接，显示"-"

2. 新增"最后连接"列，显示 `last_connected_at` 或 "-"

3. 新增"错误信息"列，显示 `connection_error`（鼠标悬停提示）

4. 连接状态使用颜色圆点 + 文字标识

**实现细节**：
```vue
<!-- 状态列修改 -->
<td>
  <span v-if="inst.is_active" 
        :class="['status-indicator', inst.is_connected ? 'status-active' : 'status-error']">
    <span class="status-dot"></span>
    {{ inst.is_connected ? '在线' : '离线' }}
  </span>
  <span v-else class="status-inactive">
    <span class="status-dot"></span>
    禁用
  </span>
</td>
<!-- 新增：最后连接时间列 -->
<td>{{ inst.last_connected_at ? formatDate(inst.last_connected_at) : '-' }}</td>
```

### 3.2 API 封装 — `frontend/src/api/index.js`

**目标**：无需修改。`getInstances()` 已返回实例全部字段，新增的 `is_connected`、`last_connected_at` 等字段会自动包含在响应中。

---

## 四、Git 发布

### 4.1 提交并推送
```bash
git add -A
git commit -m "feat: 增加SQL连接断联监控功能

- MonitoredInstance 模型新增 is_connected / last_connected_at 等连接状态字段
- 在采集周期中增加连接预检，断开时跳过采集并产生告警
- 新增 connection_lost / connection_recovered 两条内置告警规则
- 连接恢复时自动产生恢复通知
- 实例管理页展示在线/离线状态和最后连接时间
- 自动迁移：monitored_instances 表新增连接状态列"
git push origin main
```

---

## 五、验证步骤

1. **启动后端**：确认数据库迁移成功，`monitored_instances` 表新增 4 个字段
2. **启动前端**：确认实例管理页面展示连接状态列
3. **正常测试**：添加一个可连接的 SQL Server 实例，确认采集正常，状态显示"在线"
4. **断线测试**：手动断开 SQL Server 服务，等待下一个采集周期（60s），确认：
   - 实例状态变为"离线"（红色）
   - 告警页面出现 `connection_lost` 告警
   - 通知渠道收到断开告警消息
5. **恢复测试**：重新启动 SQL Server 服务，等待下一个采集周期，确认：
   - 实例状态恢复为"在线"（绿色）
   - 告警页面出现 `connection_recovered` 告警
6. **冷却期测试**：多次触发断开，确认 10 分钟内不重复产生相同告警
