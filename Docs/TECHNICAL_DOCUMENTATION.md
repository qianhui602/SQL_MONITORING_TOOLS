# SQL 监控平台 - 技术文档

## 1. 技术架构

### 1.1 整体架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                          客户端层 (Client)                          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Vue.js 3 前端应用                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │
│  │  │ Dashboard│ │ Trends   │ │ Deadlocks│ │ Alerts   │  ...    │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │ HTTP/AJAX                             │
│                              ▼                                       │
├──────────────────────────────────────────────────────────────────────┤
│                        网关层 (Gateway)                             │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Nginx 反向代理                              │  │
│  │  - 静态文件服务                                                │  │
│  │  - API 请求转发 (/api → backend:8000)                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
├──────────────────────────────────────────────────────────────────────┤
│                       应用层 (Application)                          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI 后端服务                             │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │  │
│  │  │   Routers   │ │  Services   │ │  Collectors │              │  │
│  │  │  (API 路由) │ │ (业务逻辑)  │ │ (数据采集)  │              │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘              │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │  │
│  │  │   Models    │ │  Scheduler  │ │   Config    │              │  │
│  │  │ (数据模型)  │ │ (定时任务)  │ │  (配置管理) │              │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘              │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                    │                           │                     │
│                    ▼                           ▼                     │
├──────────────────────────────────────────────────────────────────────┤
│                        数据层 (Data)                                 │
│  ┌─────────────────────┐           ┌─────────────────────┐          │
│  │    PostgreSQL 16    │           │    SQL Server       │          │
│  │  (监控数据存储)     │           │  (被监控目标)       │          │
│  └─────────────────────┘           └─────────────────────┘          │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SQL Server │───▶│  Collectors │───▶│  Scheduler  │───▶│ PostgreSQL  │
│  (数据源)   │    │  (数据采集) │    │ (定时调度)  │    │  (数据存储) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                  │                  │
                          │                  ▼                  │
                          │           ┌─────────────┐          │
                          │           │ AlertEngine │          │
                          │           │ (告警引擎)  │          │
                          │           └─────────────┘          │
                          │                  │                  │
                          │                  ▼                  │
                          │           ┌─────────────┐          │
                          │           │ Notification│          │
                          │           │ (通知服务)  │          │
                          │           └─────────────┘          │
                          │                                      │
                          ▼                                      ▼
                   ┌─────────────┐                        ┌─────────────┐
                   │   FastAPI   │◀───────────────────────│   FastAPI   │
                   │  (后端API)  │                        │  (后端API)  │
                   └─────────────┘                        └─────────────┘
                          │                                      │
                          ▼                                      ▼
                   ┌─────────────┐                        ┌─────────────┐
                   │   Vue.js    │                        │   Vue.js    │
                   │  (前端UI)   │                        │  (前端UI)   │
                   └─────────────┘                        └─────────────┘
```

### 1.3 技术栈版本

| 组件 | 技术 | 版本 |
|------|------|------|
| **后端框架** | FastAPI | 0.115.0+ |
| **ASGI 服务器** | Uvicorn | 0.30.0+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **PostgreSQL 驱动** | asyncpg | 0.29.0+ |
| **SQL Server 驱动** | pymssql | 2.3.0+ |
| **数据库迁移** | Alembic | 1.13.0+ |
| **定时任务** | APScheduler | 3.10.0+ |
| **配置管理** | pydantic-settings | 2.0.0+ |
| **密码加密** | bcrypt | 4.1.0+ |
| **JWT** | PyJWT | 2.8.0+ |
| **HTTP 客户端** | httpx | 0.27.0+ |
| **前端框架** | Vue.js | 3.4.0+ |
| **路由** | Vue Router | 4.3.0+ |
| **构建工具** | Vite | 5.4.0+ |
| **HTTP 客户端** | Axios | 1.7.0+ |
| **图表库** | ECharts | 5.5.0+ |
| **数据库** | PostgreSQL | 16 |
| **容器化** | Docker | 20.10+ |
| **容器编排** | Docker Compose | 2.0+ |
| **Web 服务器** | Nginx | 1.26+ |

## 2. 项目结构

### 2.1 后端结构

```
backend/
├── alembic/                    # 数据库迁移脚本
│   ├── versions/              # 迁移版本文件
│   ├── env.py                 # 迁移环境配置
│   └── script.py.mako         # 迁移脚本模板
├── app/                        # 应用代码
│   ├── collectors/            # 数据采集器
│   │   ├── __init__.py
│   │   ├── collector.py       # 采集协调器
│   │   ├── sqlserver.py       # SQL Server 连接管理
│   │   ├── performance.py     # 性能指标采集
│   │   ├── deadlock.py        # 死锁检测
│   │   ├── slow_query.py      # 慢查询采集
│   │   ├── blocking.py        # 阻塞进程采集
│   │   ├── disk.py            # 磁盘空间采集
│   │   └── index_analyzer.py  # 索引分析
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── performance.py     # 性能指标模型
│   │   ├── deadlock.py        # 死锁事件模型
│   │   ├── alert.py           # 告警日志模型
│   │   ├── alert_rule.py      # 告警规则模型
│   │   ├── user.py            # 用户模型
│   │   ├── instance.py        # 监控实例模型
│   │   ├── slow_query.py      # 慢查询模型
│   │   ├── blocking.py        # 阻塞事件模型
│   │   ├── disk.py            # 磁盘空间模型
│   │   ├── index_analysis.py  # 索引分析模型
│   │   ├── audit_log.py       # 审计日志模型
│   │   ├── config.py          # 系统配置模型
│   │   └── report.py          # 报告记录模型
│   ├── routers/               # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证接口
│   │   ├── users.py           # 用户管理接口
│   │   ├── metrics.py         # 性能指标接口
│   │   ├── deadlocks.py       # 死锁接口
│   │   ├── alerts.py          # 告警接口
│   │   ├── alert_rules.py     # 告警规则接口
│   │   ├── instances.py       # 实例管理接口
│   │   ├── slow_queries.py    # 慢查询接口
│   │   ├── blocking.py        # 阻塞接口
│   │   ├── disk.py            # 磁盘接口
│   │   ├── indexes.py         # 索引接口
│   │   ├── audit_logs.py      # 审计日志接口
│   │   ├── config.py          # 配置接口
│   │   ├── export.py          # 数据导出接口
│   │   ├── notifications.py   # 通知接口
│   │   ├── reports.py         # 报告接口
│   │   └── upgrade.py         # 在线升级接口
│   ├── services/              # 业务服务
│   │   ├── __init__.py
│   │   ├── auth_service.py    # 认证服务
│   │   ├── alert_service.py   # 告警服务
│   │   ├── audit_service.py   # 审计服务
│   │   ├── notification.py    # 通知服务
│   │   ├── deepseek.py        # AI 分析服务
│   │   └── upgrade_service.py # 在线升级服务
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── init_db.py             # 数据库初始化
│   ├── main.py                # 应用入口
│   └── scheduler.py           # 定时任务调度
├── .env.example               # 环境变量模板
├── Dockerfile                 # Docker 构建文件
├── alembic.ini                # Alembic 配置
└── requirements.txt           # Python 依赖
```

### 2.2 前端结构

```
frontend/
├── src/
│   ├── api/                   # API 客户端
│   │   └── index.js           # Axios 实例和 API 函数
│   ├── components/            # 公共组件
│   │   └── Layout.vue         # 布局组件
│   ├── router/                # 路由配置
│   │   └── index.js           # 路由定义
│   ├── stores/                # 状态管理
│   │   ├── auth.js            # 认证状态
│   │   └── theme.js           # 主题状态
│   ├── styles/                # 样式文件
│   │   └── theme.css          # 主题样式
│   ├── utils/                 # 工具函数
│   │   └── datetime.js        # 日期时间工具
│   ├── views/                 # 页面组件
│   │   ├── Dashboard.vue      # 仪表盘
│   │   ├── Trends.vue         # 性能趋势
│   │   ├── Deadlocks.vue      # 死锁监控
│   │   ├── Alerts.vue         # 告警管理
│   │   ├── AlertRules.vue     # 告警规则
│   │   ├── SlowQueries.vue    # 慢查询分析
│   │   ├── Blocking.vue       # 阻塞进程
│   │   ├── Disk.vue           # 磁盘空间
│   │   ├── Indexes.vue        # 索引分析
│   │   ├── Instances.vue      # 实例管理
│   │   ├── Users.vue          # 用户管理
│   │   ├── AuditLogs.vue      # 审计日志
│   │   ├── Settings.vue       # 系统设置
│   │   ├── Report.vue         # 系统报告
│   │   ├── Upgrade.vue        # 在线升级
│   │   └── Login.vue          # 登录页面
│   ├── App.vue                # 根组件
│   └── main.js                # 应用入口
├── Dockerfile                 # Docker 构建文件
├── index.html                 # HTML 入口
├── package.json               # Node.js 依赖
├── package-lock.json          # 依赖锁定文件
└── vite.config.js             # Vite 配置
```

## 3. 核心模块实现

### 3.1 数据采集模块

#### 3.1.1 采集协调器 (collector.py)

采集协调器是数据采集的核心组件，负责整合多个采集器：

```python
class MetricsCollector:
    """指标采集协调器"""
    
    def __init__(self, connection_manager: MSSQLConnectionManager = None):
        self.connection_manager = connection_manager or MSSQLConnectionManager()
        self.performance_collector = PerformanceCollector()
        self.deadlock_detector = DeadlockDetector()
        self.slow_query_collector = SlowQueryCollector()
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """执行一次完整的采集"""
        result = {
            "metrics": [],
            "deadlocks": [],
            "slow_queries": [],
        }
        
        # 获取连接
        connection = self.connection_manager.get_connection()
        
        # 采集性能指标
        perf_metrics = self.performance_collector.collect_all(connection)
        # ... 处理性能指标
        
        # 采集死锁事件
        deadlock_events = self.deadlock_detector.detect(connection)
        # ... 处理死锁事件
        
        # 采集慢查询
        slow_query_data = self.slow_query_collector.collect_slow_queries(connection)
        # ... 处理慢查询
        
        return result
```

#### 3.1.2 SQL Server 连接管理 (sqlserver.py)

连接管理器负责管理到 SQL Server 的连接：

```python
class MSSQLConnectionManager:
    """SQL Server 连接管理器"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or settings.MSSQL_HOST
        self.port = port or settings.MSSQL_PORT
        self.user = user or settings.MSSQL_USER
        self.password = password or settings.MSSQL_PASSWORD
        self.database = database or settings.MSSQL_DATABASE
        self._connection = None
    
    def get_connection(self) -> pymssql.Connection:
        """获取 SQL Server 连接（含重试机制）"""
        if self._connection and self._test_connection_alive():
            return self._connection
        
        # 重试逻辑
        for attempt in range(1, _RETRY_MAX + 1):
            try:
                self._connection = pymssql.connect(
                    server=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    timeout=10,
                    login_timeout=10,
                )
                return self._connection
            except pymssql.Error as e:
                if attempt < _RETRY_MAX:
                    time.sleep(2 ** attempt)
        
        raise MSSQLConnectionError(...)
```

#### 3.1.3 性能指标采集 (performance.py)

性能采集器从 SQL Server DMV 采集各类指标：

```python
class PerformanceCollector:
    """SQL Server 性能指标采集器"""
    
    def collect_cpu(self, connection) -> Dict[str, Any]:
        """采集 CPU 使用率"""
        # 查询 sys.dm_os_ring_buffers 获取 CPU 使用率
        pass
    
    def collect_memory(self, connection) -> Dict[str, Any]:
        """采集内存使用量"""
        # 查询 sys.dm_os_performance_counters 获取内存指标
        pass
    
    def collect_connections(self, connection) -> Dict[str, Any]:
        """采集连接信息"""
        # 查询 sys.dm_exec_sessions 获取连接数
        pass
    
    def collect_io(self, connection) -> Dict[str, Any]:
        """采集 IO 统计"""
        # 查询 sys.dm_io_virtual_file_stats 获取 IO 指标
        pass
```

#### 3.1.4 死锁检测 (deadlock.py)

死锁检测器从 SQL Server 系统健康会话捕获死锁事件：

```python
class DeadlockDetector:
    """死锁事件检测器"""
    
    def detect(self, connection) -> List[Dict[str, Any]]:
        """检测死锁事件"""
        # 查询 system_health 会话中的 xml_deadlock_report
        # 解析死锁 XML，提取相关信息
        pass
```

### 3.2 定时任务调度 (scheduler.py)

调度器使用 APScheduler 管理定时采集任务：

```python
class SchedulerManager:
    """APScheduler 调度器管理器"""
    
    def setup(self, app, settings: Settings):
        """配置调度器"""
        self.scheduler = AsyncIOScheduler()
        self._alert_engine = AlertEngine(db_session_factory=async_session_factory)
        
        interval = settings.SCHEDULER_INTERVAL_SECONDS
        self.add_collect_job(interval_seconds=interval)
    
    async def _collect_and_store(self):
        """采集任务：遍历所有活跃实例采集指标并写入 PostgreSQL"""
        # 加载运行时配置
        runtime_config = await self._load_runtime_config()
        
        # 判断是否启用多实例模式
        instances_enabled = runtime_config.get("mssql_instances_enabled", "false").lower() == "true"
        
        if instances_enabled:
            await self._collect_multi_instance(runtime_config)
        else:
            await self._collect_single_instance(runtime_config)
    
    async def _collect_multi_instance(self, runtime_config):
        """多实例采集模式"""
        instances = await self._load_active_instances()
        
        for instance in instances:
            # 为每个实例创建独立的连接管理器
            conn_mgr = MSSQLConnectionManager.get_connection_for_instance(...)
            collector = MetricsCollector(connection_manager=conn_mgr)
            data = collector.collect_all_metrics()
            
            # 存储数据
            await self._store_metrics(session, data["metrics"], server_address)
            await self._store_deadlocks(session, data["deadlocks"], server_address)
            await self._store_slow_queries(session, data["slow_queries"], server_address)
        
        # 执行告警检查
        await self._run_alert_checks(aggregated_data)
```

### 3.3 告警引擎 (alert_service.py)

告警引擎负责检查告警规则并触发告警：

```python
class AlertEngine:
    """告警规则引擎"""
    
    def __init__(self, db_session_factory):
        self.session_factory = db_session_factory
        self.notification_service = NotificationService()
        
        # 内置告警规则
        self._builtin_rules = [
            AlertRule(
                alert_type="memory_high",
                severity="critical",
                condition_func=self._condition_memory_high,
                message_template="...",
                cooldown_minutes=10,
            ),
            AlertRule(
                alert_type="deadlock_detected",
                severity="high",
                condition_func=self._condition_deadlock,
                message_template="...",
                cooldown_minutes=5,
            ),
            AlertRule(
                alert_type="collection_interrupted",
                severity="high",
                condition_func=self._condition_collection_interrupted,
                message_template="...",
                cooldown_minutes=15,
            ),
        ]
    
    async def process_metrics(self, metrics_data: Dict[str, Any]) -> List[AlertLog]:
        """执行完整告警流程"""
        # 1. 检查内置规则
        triggered = await self.check_rules(metrics_data)
        
        # 2. 加载并检查自定义规则
        custom_triggered = await self._check_custom_rules(metrics_data)
        triggered.extend(custom_triggered)
        
        # 3. 检查冷却期 → 创建告警
        for alert_type, severity, message in triggered:
            cooldown = self._get_cooldown_minutes(alert_type)
            if await self._is_in_cooldown(alert_type, cooldown):
                continue
            alert = await self.create_alert(alert_type, severity, message)
        
        return created_alerts
```

### 3.4 通知服务 (notification.py)

通知服务支持多种通知渠道：

```python
class NotificationService:
    """组合通知服务"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.dingtalk_notifier = DingTalkNotifier()
        self.wecom_notifier = WeComNotifier()
    
    async def notify_all(self, subject: str, body: str) -> Dict[str, bool]:
        """同时发送所有渠道通知"""
        result = {
            "email": False,
            "dingtalk": False,
            "wecom": False,
        }
        
        # 邮件同步发送
        result["email"] = self.email_notifier.send(subject, body)
        
        # 钉钉异步发送
        result["dingtalk"] = await self.dingtalk_notifier.send(body)
        
        # 企业微信异步发送
        result["wecom"] = await self.wecom_notifier.send(body)
        
        return result
```

### 3.5 认证服务 (auth_service.py)

认证服务提供 JWT 认证和权限控制：

```python
class AuthService:
    """认证服务"""
    
    @staticmethod
    def hash_password(plain: str) -> str:
        """使用 bcrypt 哈希密码"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    
    @staticmethod
    def create_access_token(user_id: int, username: str, role: str) -> str:
        """生成 JWT access token"""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "iat": now,
            "exp": now + timedelta(hours=settings.JWT_EXPIRE_HOURS),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """解码 JWT token"""
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None
```

### 3.6 AI 分析服务 (deepseek.py)

AI 分析服务集成 DeepSeek API 进行智能分析：

```python
async def analyze_deadlock(deadlock_info: dict) -> Optional[str]:
    """使用 DeepSeek AI 分析死锁"""
    prompt = _build_prompt(deadlock_info)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位资深的 SQL Server 数据库性能优化专家...",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
        )
        
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()
```

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │  system_configs │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ username        │       │ config_key      │
│ password_hash   │       │ config_value    │
│ role            │       │ description     │
│ full_name       │       │ created_at      │
│ is_active       │       │ updated_at      │
│ last_login_at   │       └─────────────────┘
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│  audit_logs     │       │monitored_instances│
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ name            │
│ username        │       │ host            │
│ action          │       │ port            │
│ detail          │       │ username        │
│ ip_address      │       │ password        │
│ created_at      │       │ database_name   │
└─────────────────┘       │ is_active       │
                          │ description     │
                          │ created_at      │
                          │ updated_at      │
                          └─────────────────┘
                                   │
                                   │ 1:N
                                   ▼
┌─────────────────┐       ┌─────────────────┐
│    metrics      │       │   deadlocks     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ category        │       │ occur_at        │
│ metric_name     │       │ deadlock_xml    │
│ metric_value    │       │ victim_session_id│
│ unit            │       │ server_address  │
│ collected_at    │       │ analysis_result │
│ server_address  │       │ created_at      │
│ created_at      │       └─────────────────┘
└─────────────────┘                │
                                   │ 1:N
                                   ▼
                          ┌─────────────────┐
                          │  deadlock_sqls  │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ event_id (FK)   │
                          │ session_id      │
                          │ sql_text        │
                          │ isolation_level │
                          │ involved_objects│
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  alert_logs     │       │  alert_rules    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ alert_type      │       │ name            │
│ severity        │       │ description     │
│ message         │       │ metric_category │
│ triggered_at    │       │ metric_name     │
│ acknowledged    │       │ operator        │
│ acknowledged_at │       │ threshold       │
│ notification_sent│      │ severity        │
│ created_at      │       │ enabled         │
└─────────────────┘       │ silence_start   │
                          │ silence_end     │
                          │ created_at      │
                          │ updated_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  slow_queries   │       │blocking_events  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ sql_hash        │       │ blocking_session_id│
│ sql_text        │       │ blocked_session_id│
│ execution_count │       │ blocking_sql_text│
│ total_cpu_ms    │       │ blocked_sql_text │
│ total_logical_reads│    │ wait_time_seconds│
│ total_elapsed_ms│       │ wait_type       │
│ avg_elapsed_ms  │       │ server_address  │
│ last_execution_time│    │ collected_at    │
│ collected_at    │       │ created_at      │
│ server_address  │       └─────────────────┘
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│disk_space_records│      │missing_indexes  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ database_name   │       │ database_name   │
│ file_type       │       │ table_name      │
│ file_name       │       │ equality_columns│
│ physical_name   │       │ inequality_columns│
│ size_mb         │       │ included_columns│
│ used_mb         │       │ avg_total_user_cost│
│ free_mb         │       │ avg_user_impact │
│ usage_pct       │       │ user_seeks      │
│ server_address  │       │ user_scans      │
│ collected_at    │       │ server_address  │
│ created_at      │       │ collected_at    │
└─────────────────┘       │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│index_fragmentation│     │ report_records  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ database_name   │       │ title           │
│ table_name      │       │ content         │
│ index_name      │       │ report_data     │
│ index_type      │       │ ai_analysis     │
│ avg_fragmentation_pct│  │ created_at      │
│ page_count      │       └─────────────────┘
│ server_address  │
│ collected_at    │
│ created_at      │
└─────────────────┘
```

### 4.2 索引设计

```sql
-- 性能指标表索引
CREATE INDEX idx_metrics_collected_at ON metrics(collected_at);
CREATE INDEX idx_metrics_category ON metrics(category);
CREATE INDEX idx_metrics_server_address ON metrics(server_address);
CREATE INDEX idx_metrics_category_name_collected ON metrics(category, metric_name, collected_at);

-- 死锁事件表索引
CREATE INDEX idx_deadlocks_occur_at ON deadlocks(occur_at);
CREATE INDEX idx_deadlocks_server_address ON deadlocks(server_address);

-- 告警日志表索引
CREATE INDEX idx_alert_logs_triggered_at ON alert_logs(triggered_at);
CREATE INDEX idx_alert_logs_alert_type ON alert_logs(alert_type);
CREATE INDEX idx_alert_logs_severity ON alert_logs(severity);

-- 慢查询表索引
CREATE INDEX idx_slow_queries_collected_at ON slow_queries(collected_at);
CREATE INDEX idx_slow_queries_server_address ON slow_queries(server_address);
CREATE INDEX idx_slow_queries_sql_hash ON slow_queries(sql_hash);

-- 用户表索引
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- 审计日志表索引
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

## 5. API 设计

### 5.1 RESTful API 规范

- 使用标准 HTTP 方法：GET、POST、PUT、DELETE
- 使用 JSON 格式进行数据交换
- 使用 HTTP 状态码表示请求结果
- 使用 JWT 进行身份验证
- 所有 API 以 `/api` 为前缀

### 5.2 认证流程

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │                    │ Database │
└────┬─────┘                    └────┬─────┘                    └────┬─────┘
     │                               │                               │
     │  1. POST /api/auth/login      │                               │
     │  {username, password}         │                               │
     │──────────────────────────────▶│                               │
     │                               │  2. 查询用户                  │
     │                               │──────────────────────────────▶│
     │                               │  3. 返回用户信息              │
     │                               │◀──────────────────────────────│
     │                               │                               │
     │                               │  4. 验证密码                  │
     │                               │  5. 生成 JWT                  │
     │                               │                               │
     │  6. 返回 {access_token, user} │                               │
     │◀──────────────────────────────│                               │
     │                               │                               │
     │  7. GET /api/metrics/realtime │                               │
     │  Authorization: Bearer <token>│                               │
     │──────────────────────────────▶│                               │
     │                               │  8. 验证 JWT                  │
     │                               │  9. 查询数据                  │
     │                               │──────────────────────────────▶│
     │                               │  10. 返回数据                 │
     │                               │◀──────────────────────────────│
     │  11. 返回指标数据             │                               │
     │◀──────────────────────────────│                               │
     │                               │                               │
```

### 5.3 API 端点详细说明

#### 5.3.1 认证接口

**POST /api/auth/login**
- 描述：用户登录
- 请求体：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- 响应：
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "string",
      "role": "string",
      "full_name": "string"
    }
  }
  ```

**GET /api/auth/me**
- 描述：获取当前用户信息
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string",
    "full_name": "string",
    "is_active": true,
    "last_login_at": "2024-01-01T00:00:00Z"
  }
  ```

**POST /api/auth/change_password**
- 描述：修改密码
- 请求头：`Authorization: Bearer <token>`
- 请求体：
  ```json
  {
    "old_password": "string",
    "new_password": "string"
  }
  ```
- 响应：
  ```json
  {
    "message": "密码修改成功"
  }
  ```

#### 5.3.2 性能指标接口

**GET /api/metrics/realtime**
- 描述：获取实时指标
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  {
    "cpu": {
      "cpu_usage": 45.2,
      "sql_cpu": 45.2
    },
    "memory": {
      "sql_server_memory_mb": 8192,
      "buffer_cache_hit_ratio": 99.5,
      "target_memory_mb": 16384,
      "page_life_expectancy": 3600
    },
    "connection": {
      "active_sessions": 50,
      "user_connections": 45
    },
    "io": {
      "read_bytes_per_sec": 1024000,
      "write_bytes_per_sec": 512000
    },
    "server_address": "10.0.0.1:1433"
  }
  ```

**GET /api/metrics/history**
- 描述：获取历史指标
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `category` (必填)：指标分类
  - `metric_name` (可选)：指标名称
  - `start_time` (必填)：起始时间
  - `end_time` (必填)：结束时间
  - `limit` (可选)：返回记录数上限，默认 1000
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "collected_at": "2024-01-01T00:00:00Z",
      "metric_value": 45.2,
      "metric_name": "cpu_usage"
    }
  ]
  ```

**GET /api/metrics/summary**
- 描述：获取指标摘要
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  {
    "cpu_usage": 45.2,
    "sql_server_memory_mb": 8192,
    "active_sessions": 50,
    "buffer_cache_hit_ratio": 99.5,
    "memory_usage_pct": 75.0,
    "server_address": "10.0.0.1:1433"
  }
  ```

#### 5.3.3 死锁接口

**GET /api/deadlocks**
- 描述：获取死锁列表
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `limit` (可选)：返回记录数上限
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "id": 1,
      "occur_at": "2024-01-01T00:00:00Z",
      "victim_session_id": 55,
      "server_address": "10.0.0.1:1433",
      "analysis_result": null
    }
  ]
  ```

**GET /api/deadlocks/{id}**
- 描述：获取死锁详情
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "id": 1,
    "occur_at": "2024-01-01T00:00:00Z",
    "deadlock_xml": "<deadlock>...</deadlock>",
    "victim_session_id": 55,
    "server_address": "10.0.0.1:1433",
    "analysis_result": "...",
    "deadlock_sqls": [
      {
        "session_id": 55,
        "sql_text": "SELECT * FROM table1",
        "isolation_level": "READ COMMITTED",
        "involved_objects": "table1, table2"
      }
    ]
  }
  ```

**POST /api/deadlocks/{id}/analyze**
- 描述：AI 分析死锁
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "analysis_result": "..."
  }
  ```

#### 5.3.4 告警接口

**GET /api/alerts**
- 描述：获取告警列表
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `severity` (可选)：严重级别
  - `limit` (可选)：返回记录数上限
- 响应：
  ```json
  [
    {
      "id": 1,
      "alert_type": "memory_high",
      "severity": "critical",
      "message": "...",
      "triggered_at": "2024-01-01T00:00:00Z",
      "acknowledged": false,
      "notification_sent": true
    }
  ]
  ```

**PUT /api/alerts/{id}/acknowledge**
- 描述：确认告警
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "告警已确认"
  }
  ```

#### 5.3.5 告警规则接口

**GET /api/alert-rules**
- 描述：获取告警规则列表
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  [
    {
      "id": 1,
      "name": "内存使用率过高",
      "description": "内存使用率超过 85% 时触发告警",
      "metric_category": "os_memory",
      "metric_name": "memory_usage_pct",
      "operator": "gt",
      "threshold": 85,
      "severity": "critical",
      "enabled": true,
      "silence_start": null,
      "silence_end": null
    }
  ]
  ```

**POST /api/alert-rules**
- 描述：创建告警规则
- 请求头：`Authorization: Bearer <token>`
- 请求体：
  ```json
  {
    "name": "string",
    "description": "string",
    "metric_category": "string",
    "metric_name": "string",
    "operator": "gt|lt|gte|lte|eq",
    "threshold": 0,
    "severity": "low|medium|high|critical",
    "enabled": true,
    "silence_start": "HH:MM:SS",
    "silence_end": "HH:MM:SS"
  }
  ```
- 响应：
  ```json
  {
    "id": 1,
    "name": "string",
    ...
  }
  ```

**PUT /api/alert-rules/{id}**
- 描述：更新告警规则
- 请求头：`Authorization: Bearer <token>`
- 请求体：同创建
- 响应：同创建

**DELETE /api/alert-rules/{id}**
- 描述：删除告警规则
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "告警规则已删除"
  }
  ```

**PUT /api/alert-rules/{id}/toggle**
- 描述：启用/禁用告警规则
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "id": 1,
    "enabled": true
  }
  ```

#### 5.3.6 实例管理接口

**GET /api/instances**
- 描述：获取实例列表
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  [
    {
      "id": 1,
      "name": "生产环境",
      "host": "10.0.0.1",
      "port": 1433,
      "username": "sa",
      "database_name": "master",
      "is_active": true,
      "description": "生产环境 SQL Server"
    }
  ]
  ```

**POST /api/instances**
- 描述：创建实例
- 请求头：`Authorization: Bearer <token>`
- 请求体：
  ```json
  {
    "name": "string",
    "host": "string",
    "port": 1433,
    "username": "string",
    "password": "string",
    "database_name": "string",
    "is_active": true,
    "description": "string"
  }
  ```
- 响应：同获取实例列表中的单个对象

**PUT /api/instances/{id}**
- 描述：更新实例
- 请求头：`Authorization: Bearer <token>`
- 请求体：同创建
- 响应：同创建

**DELETE /api/instances/{id}**
- 描述：删除实例
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "实例已删除"
  }
  ```

**POST /api/instances/{id}/test**
- 描述：测试实例连接
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "success": true,
    "message": "连接成功"
  }
  ```

#### 5.3.7 慢查询接口

**GET /api/slow-queries**
- 描述：获取慢查询列表
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `limit` (可选)：返回记录数上限
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "id": 1,
      "sql_hash": "0x1234567890",
      "sql_text": "SELECT * FROM table1 WHERE ...",
      "execution_count": 100,
      "total_cpu_ms": 5000,
      "total_logical_reads": 100000,
      "total_elapsed_ms": 10000,
      "avg_elapsed_ms": 100,
      "last_execution_time": "2024-01-01T00:00:00Z",
      "server_address": "10.0.0.1:1433"
    }
  ]
  ```

**GET /api/slow-queries/stats**
- 描述：获取慢查询统计
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  {
    "total_count": 100,
    "avg_duration_ms": 150,
    "max_duration_ms": 5000,
    "top_queries": [...]
  }
  ```

#### 5.3.8 阻塞接口

**GET /api/blocking/realtime**
- 描述：获取实时阻塞
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "blocking_session_id": 55,
      "blocked_session_id": 66,
      "blocking_sql_text": "UPDATE table1 SET ...",
      "blocked_sql_text": "SELECT * FROM table1 WHERE ...",
      "wait_time_seconds": 30,
      "wait_type": "LCK_M_S"
    }
  ]
  ```

**GET /api/blocking/history**
- 描述：获取阻塞历史
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `limit` (可选)：返回记录数上限
  - `server_address` (可选)：按实例筛选
- 响应：同实时阻塞

#### 5.3.9 磁盘接口

**GET /api/disk/space**
- 描述：获取磁盘空间
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "database_name": "master",
      "file_type": "ROWS",
      "file_name": "master.mdf",
      "physical_name": "C:\\Data\\master.mdf",
      "size_mb": 100,
      "used_mb": 80,
      "free_mb": 20,
      "usage_pct": 80.0
    }
  ]
  ```

**GET /api/disk/history**
- 描述：获取磁盘历史
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `database_name` (可选)：数据库名称
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `server_address` (可选)：按实例筛选
- 响应：同磁盘空间

#### 5.3.10 索引接口

**GET /api/indexes/missing**
- 描述：获取缺失索引
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `limit` (可选)：返回记录数上限
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "database_name": "master",
      "table_name": "table1",
      "equality_columns": "col1, col2",
      "inequality_columns": "col3",
      "included_columns": "col4, col5",
      "avg_total_user_cost": 100.5,
      "avg_user_impact": 95.0,
      "user_seeks": 1000,
      "user_scans": 100
    }
  ]
  ```

**GET /api/indexes/fragmentation**
- 描述：获取索引碎片
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `database_name` (可选)：数据库名称
  - `threshold` (可选)：碎片率阈值
  - `limit` (可选)：返回记录数上限
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  [
    {
      "database_name": "master",
      "table_name": "table1",
      "index_name": "IX_table1_col1",
      "index_type": "NONCLUSTERED",
      "avg_fragmentation_pct": 85.5,
      "page_count": 10000
    }
  ]
  ```

#### 5.3.11 审计日志接口

**GET /api/audit-logs**
- 描述：获取审计日志
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `user_id` (可选)：用户 ID
  - `action` (可选)：操作类型
  - `limit` (可选)：返回记录数上限
- 响应：
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin",
      "action": "login",
      "detail": "用户登录成功",
      "ip_address": "192.168.1.1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
  ```

#### 5.3.12 数据导出接口

**GET /api/export/metrics**
- 描述：导出指标数据
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (必填)：起始时间
  - `end_time` (必填)：结束时间
  - `category` (可选)：指标分类
  - `server_address` (可选)：按实例筛选
- 响应：CSV 文件

**GET /api/export/alerts**
- 描述：导出告警数据
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (必填)：起始时间
  - `end_time` (必填)：结束时间
  - `severity` (可选)：严重级别
- 响应：CSV 文件

**GET /api/export/deadlocks**
- 描述：导出死锁数据
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (必填)：起始时间
  - `end_time` (必填)：结束时间
  - `server_address` (可选)：按实例筛选
- 响应：CSV 文件

**GET /api/export/slow-queries**
- 描述：导出慢查询数据
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (必填)：起始时间
  - `end_time` (必填)：结束时间
  - `server_address` (可选)：按实例筛选
- 响应：CSV 文件

#### 5.3.13 通知接口

**GET /api/notifications**
- 描述：获取通知列表
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `limit` (可选)：返回记录数上限，默认 20
- 响应：
  ```json
  [
    {
      "id": 1,
      "alert_type": "memory_high",
      "severity": "critical",
      "message": "...",
      "triggered_at": "2024-01-01T00:00:00Z",
      "read": false
    }
  ]
  ```

**PUT /api/notifications/{id}/read**
- 描述：标记通知已读
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "通知已标记为已读"
  }
  ```

**DELETE /api/notifications/{id}**
- 描述：删除通知
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "通知已删除"
  }
  ```

**POST /api/notifications/read-all**
- 描述：标记所有通知已读
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "所有通知已标记为已读"
  }
  ```

#### 5.3.14 报告接口

**GET /api/reports/summary**
- 描述：获取报告摘要
- 请求头：`Authorization: Bearer <token>`
- 查询参数：
  - `start_time` (可选)：起始时间
  - `end_time` (可选)：结束时间
  - `server_address` (可选)：按实例筛选
- 响应：
  ```json
  {
    "summary": {
      "cpu_usage": 45.2,
      "sql_server_memory_mb": 8192,
      "active_sessions": 50,
      "buffer_cache_hit_ratio": 99.5,
      "page_life_expectancy": 3600,
      "lock_waits": 10
    },
    "deadlocks": {
      "count": 5,
      "latest_time": "2024-01-01T00:00:00Z"
    },
    "slow_queries": {
      "count": 100,
      "avg_duration_ms": 150,
      "top_queries": [...]
    },
    "blocking": {
      "count": 20
    },
    "disk": {
      "usage_pct": 75.0
    },
    "indexes": {
      "missing_count": 10,
      "high_fragmentation_count": 5
    }
  }
  ```

**POST /api/reports/save**
- 描述：保存报告
- 请求头：`Authorization: Bearer <token>`
- 请求体：
  ```json
  {
    "title": "string",
    "content": "string",
    "report_data": {},
    "ai_analysis": "string"
  }
  ```
- 响应：
  ```json
  {
    "id": 1,
    "title": "string",
    ...
  }
  ```

**GET /api/reports/history**
- 描述：获取报告历史
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  [
    {
      "id": 1,
      "title": "string",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
  ```

**DELETE /api/reports/history/{id}**
- 描述：删除报告
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "message": "报告已删除"
  }
  ```

#### 5.3.15 配置接口

**GET /api/config**
- 描述：获取所有配置
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  [
    {
      "id": 1,
      "config_key": "mssql_host",
      "config_value": "10.0.0.1",
      "description": "SQL Server 服务器地址"
    }
  ]
  ```

**GET /api/config/{key}**
- 描述：获取单个配置
- 请求头：`Authorization: Bearer <token>`
- 响应：
  ```json
  {
    "id": 1,
    "config_key": "mssql_host",
    "config_value": "10.0.0.1",
    "description": "SQL Server 服务器地址"
  }
  ```

**PUT /api/config/{key}**
- 描述：更新配置
- 请求头：`Authorization: Bearer <token>`
- 请求体：
  ```json
  {
    "config_value": "string"
  }
  ```
- 响应：
  ```json
  {
    "id": 1,
    "config_key": "mssql_host",
    "config_value": "10.0.0.2",
    "description": "SQL Server 服务器地址"
  }
  ```

## 6. 前端架构

### 6.1 组件结构

```
App.vue
└── Layout.vue
    ├── Sidebar (侧边栏)
    │   ├── Logo
    │   ├── Navigation Menu
    │   └── Collapse Button
    ├── Topbar (顶部栏)
    │   ├── Page Title
    │   ├── Notification Bell
    │   ├── Theme Toggle
    │   └── User Menu
    └── Main Content (主内容区)
        ├── Dashboard.vue
        ├── Trends.vue
        ├── Deadlocks.vue
        ├── Alerts.vue
        ├── AlertRules.vue
        ├── SlowQueries.vue
        ├── Blocking.vue
        ├── Disk.vue
        ├── Indexes.vue
        ├── Instances.vue
        ├── Users.vue
        ├── AuditLogs.vue
        ├── Settings.vue
        ├── Report.vue
        └── Login.vue
```

### 6.2 路由配置

```javascript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true, layout: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '总览', icon: 'dashboard' }
  },
  // ... 其他路由
]

// 路由守卫
router.beforeEach((to, from, next) => {
  const isPublic = to.meta?.public
  const authed = authStore.isAuthenticated.value

  // 未登录用户访问受保护页面时重定向到登录页
  if (!isPublic && !authed) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // 非管理员访问需要管理员权限的页面时重定向到仪表盘
  if (to.meta?.requiresAdmin && !authStore.isAdmin.value) {
    return next({ path: '/dashboard' })
  }

  // 已登录用户访问登录页时重定向到仪表盘
  if (to.path === '/login' && authed) {
    return next({ path: '/dashboard' })
  }

  next()
})
```

### 6.3 状态管理

使用 Vue 3 的响应式 API 进行状态管理：

```javascript
// stores/auth.js
import { reactive, computed } from 'vue'

const state = reactive({
  user: getStoredUser()
})

export const authStore = {
  state,

  isAuthenticated: computed(() => !!state.user),

  isAdmin: computed(
    () =>
      state.user &&
      (state.user.role === 'admin' || state.user.role === 'super_admin')
  ),

  isSuperAdmin: computed(
    () => state.user && state.user.role === 'super_admin'
  ),

  isViewer: computed(() => state.user && state.user.role === 'viewer'),

  roleLabel: computed(() => {
    if (!state.user) return ''
    const map = {
      super_admin: '超级管理员',
      admin: '管理员',
      viewer: '只读用户'
    }
    return map[state.user.role] || state.user.role
  }),

  async login(username, password) {
    const data = await apiLogin(username, password)
    setToken(data.access_token)
    setStoredUser(data.user)
    state.user = data.user
    return data.user
  },

  async refreshMe() {
    try {
      const me = await getMe()
      setStoredUser(me)
      state.user = me
      return me
    } catch (e) {
      this.logout()
      return null
    }
  },

  logout() {
    clearAuth()
    state.user = null
  }
}
```

### 6.4 API 客户端

```javascript
// api/index.js
import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加 JWT token
request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理 401 错误
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 函数
export function getRealtimeMetrics() {
  return request.get('/metrics/realtime')
}

export function getHistoryMetrics(params) {
  return request.get('/metrics/history', { params })
}

// ... 其他 API 函数
```

### 6.5 图表组件

使用 ECharts 进行数据可视化：

```vue
<template>
  <div class="chart-container">
    <v-chart :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const chartOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['CPU 使用率', '内存使用率']
  },
  xAxis: {
    type: 'time'
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU 使用率',
      type: 'line',
      data: []
    },
    {
      name: '内存使用率',
      type: 'line',
      data: []
    }
  ]
})
</script>
```

## 7. 部署架构

### 7.1 Docker Compose 部署

```yaml
# docker-compose.yml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: sql-monitor-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${PG_DATABASE:-sql_monitor}
      POSTGRES_USER: ${PG_USER:-postgres}
      POSTGRES_PASSWORD: ${PG_PASSWORD:-your_pg_password_here}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - monitoring-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${PG_USER:-postgres} -d ${PG_DATABASE:-sql_monitor}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sql-monitor-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - PG_HOST=postgres
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - monitoring-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sql-monitor-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - monitoring-network

volumes:
  pgdata:
    name: sql-monitor-pgdata

networks:
  monitoring-network:
    name: sql-monitor-network
    driver: bridge
```

### 7.2 后端 Dockerfile

```dockerfile
# 多阶段构建
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    freetds-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.12-slim

WORKDIR /app

# 安装运行时系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libct4 \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.3 前端 Dockerfile

```dockerfile
# 构建阶段
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:1.26-alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 7.4 Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;

    # 静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 8. 性能优化

### 8.1 后端优化

1. **异步处理**：使用 FastAPI 的异步特性，提高并发处理能力
2. **连接池**：使用 SQLAlchemy 的连接池，减少数据库连接开销
3. **缓存**：对频繁查询的数据进行缓存
4. **批量操作**：使用批量插入减少数据库交互次数
5. **索引优化**：确保数据库表有适当的索引

### 8.2 前端优化

1. **代码分割**：使用 Vite 的代码分割功能，按需加载组件
2. **图片优化**：使用适当的图片格式和压缩
3. **缓存**：利用浏览器缓存减少请求
4. **懒加载**：对非首屏组件进行懒加载
5. **虚拟滚动**：对大数据列表使用虚拟滚动

### 8.3 数据库优化

1. **索引优化**：
   - 为常用查询字段创建索引
   - 使用复合索引优化多字段查询
   - 定期分析索引使用情况

2. **查询优化**：
   - 使用 EXPLAIN ANALYZE 分析查询计划
   - 避免 SELECT *，只查询需要的字段
   - 使用 LIMIT 限制返回记录数

3. **数据清理**：
   - 定期清理历史数据
   - 使用分区表管理大数据量

## 9. 安全设计

### 9.1 认证安全

1. **密码加密**：使用 bcrypt 加密存储密码
2. **JWT 令牌**：使用 JWT 进行身份验证
3. **令牌过期**：设置合理的令牌过期时间
4. **HTTPS**：生产环境使用 HTTPS

### 9.2 接口安全

1. **权限控制**：基于角色的权限控制
2. **输入验证**：使用 Pydantic 进行输入验证
3. **SQL 注入防护**：使用参数化查询
4. **XSS 防护**：对输出进行转义

### 9.3 数据安全

1. **敏感信息加密**：对敏感配置进行加密存储
2. **访问控制**：限制数据库访问权限
3. **审计日志**：记录所有关键操作
4. **数据备份**：定期备份数据

## 10. 监控与运维

### 10.1 健康检查

```python
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": settings.PROJECT_NAME}
```

### 10.2 日志配置

```python
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
```

### 10.3 性能监控

1. **请求延迟**：监控 API 请求延迟
2. **错误率**：监控 API 错误率
3. **数据库连接**：监控数据库连接池使用情况
4. **系统资源**：监控 CPU、内存、磁盘使用情况

### 10.4 告警配置

1. **服务宕机**：监控服务是否正常运行
2. **性能下降**：监控 API 响应时间
3. **错误增多**：监控错误日志
4. **资源不足**：监控系统资源使用情况

## 11. 测试策略

### 11.1 单元测试

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "SQL 监控平台"}

def test_login():
    response = client.post("/api/auth/login", json={
        "username": "Admin",
        "password": "Chuz0001"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 11.2 集成测试

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_metrics_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 先登录获取 token
        login_response = await client.post("/api/auth/login", json={
            "username": "Admin",
            "password": "Chuz0001"
        })
        token = login_response.json()["access_token"]
        
        # 测试获取实时指标
        response = await client.get(
            "/api/metrics/realtime",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

### 11.3 端到端测试

```javascript
// tests/e2e/specs/login.js
describe('Login', () => {
  it('should login successfully', () => {
    cy.visit('/login')
    cy.get('input[name="username"]').type('Admin')
    cy.get('input[name="password"]').type('Chuz0001')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })
})
```

## 12. 常见问题

### 12.1 连接问题

**Q: 无法连接到 SQL Server**
A: 检查以下配置：
1. SQL Server 是否允许远程连接
2. 防火墙是否开放 1433 端口
3. SQL Server 是否启用 TCP/IP 协议
4. 用户名和密码是否正确

**Q: 无法连接到 PostgreSQL**
A: 检查以下配置：
1. PostgreSQL 是否允许远程连接
2. 防火墙是否开放 5432 端口
3. pg_hba.conf 是否允许连接
4. 用户名和密码是否正确

### 12.2 性能问题

**Q: 采集间隔设置为多少合适**
A: 根据实际需求设置：
- 生产环境：60-300 秒
- 测试环境：10-60 秒
- 开发环境：5-10 秒

**Q: 历史数据保留多久**
A: 建议：
- 性能指标：保留 30-90 天
- 死锁事件：保留 90-180 天
- 告警日志：保留 90-180 天
- 审计日志：保留 180-365 天

### 12.3 告警问题

**Q: 告警没有触发**
A: 检查以下配置：
1. 告警规则是否启用
2. 告警阈值是否合理
3. 是否处于静默时段
4. 是否处于冷却期

**Q: 告警通知没有发送**
A: 检查以下配置：
1. 通知渠道是否配置正确
2. SMTP 服务器是否正常
3. 钉钉/企业微信 Webhook 是否有效
4. 网络是否正常

## 13. 版本历史

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基本监控功能
- 实现告警管理功能
- 实现用户管理功能

### v1.1.0 (2024-02-01)
- 新增慢查询分析功能
- 新增阻塞进程监控功能
- 新增磁盘空间监控功能
- 新增索引分析功能

### v1.2.0 (2024-03-01)
- 新增多实例监控支持
- 新增 AI 分析功能
- 新增报告生成功能
- 优化性能和稳定性

### v1.3.0 (2024-04-01)
- 新增企业微信通知支持
- 新增数据导出功能
- 新增审计日志功能
- 优化用户体验

## 14. 未来规划

### 14.1 功能扩展
1. **更多数据库支持**：支持 MySQL、Oracle 等数据库
2. **更丰富的图表**：支持更多类型的图表
3. **更智能的告警**：基于机器学习的异常检测
4. **更完善的报告**：支持自定义报告模板

### 14.2 性能优化
1. **数据压缩**：对历史数据进行压缩存储
2. **分库分表**：支持大数据量的分库分表
3. **读写分离**：支持数据库读写分离
4. **缓存优化**：引入 Redis 缓存

### 14.3 运维优化
1. **自动化部署**：支持 CI/CD 自动化部署
2. **容器编排**：支持 Kubernetes 部署
3. **监控告警**：完善运维监控体系
4. **日志分析**：引入 ELK 日志分析