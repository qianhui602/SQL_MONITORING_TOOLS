# SQL Monitoring Platform - Technical Documentation

[简体中文](../TECHNICAL_DOCUMENTATION.md) | **English**

## 1. Technical Architecture

### 1.1 Overall Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Vue.js 3 Frontend Application               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │
│  │  │ Dashboard│ │ Trends   │ │ Deadlocks│ │ Alerts   │  ...    │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │ HTTP/AJAX                             │
│                              ▼                                       │
├──────────────────────────────────────────────────────────────────────┤
│                          Gateway Layer                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Nginx Reverse Proxy                         │  │
│  │  - Static file serving                                        │  │
│  │  - API request forwarding (/api → backend:8000)               │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
├──────────────────────────────────────────────────────────────────────┤
│                       Application Layer                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Backend Service                     │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │  │
│  │  │   Routers   │ │  Services   │ │  Collectors │              │  │
│  │  │ (API routes)│ │(business)   │ │ (collection)│              │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘              │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │  │
│  │  │   Models    │ │  Scheduler  │ │   Config    │              │  │
│  │  │(data models)│ │ (scheduler) │ │ (config)    │              │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘              │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                    │                           │                     │
│                    ▼                           ▼                     │
├──────────────────────────────────────────────────────────────────────┤
│                           Data Layer                                 │
│  ┌─────────────────────┐           ┌─────────────────────┐          │
│  │    PostgreSQL 16    │           │    SQL Server       │          │
│  │  (monitoring data)  │           │  (monitored target) │          │
│  └─────────────────────┘           └─────────────────────┘          │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SQL Server │───▶│  Collectors │───▶│  Scheduler  │───▶│ PostgreSQL  │
│  (data src) │    │(collection) │    │ (scheduler) │    │  (storage)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                  │                  │
                          │                  ▼                  │
                          │           ┌─────────────┐          │
                          │           │ AlertEngine │          │
                          │           │ (alert)     │          │
                          │           └─────────────┘          │
                          │                  │                  │
                          │                  ▼                  │
                          │           ┌─────────────┐          │
                          │           │ Notification│          │
                          │           │ (notify)    │          │
                          │           └─────────────┘          │
                          │                                      │
                          ▼                                      ▼
                   ┌─────────────┐                        ┌─────────────┐
                   │   FastAPI   │◀───────────────────────│   FastAPI   │
                   │  (backend)  │                        │  (backend)  │
                   └─────────────┘                        └─────────────┘
                          │                                      │
                          ▼                                      ▼
                   ┌─────────────┐                        ┌─────────────┐
                   │   Vue.js    │                        │   Vue.js    │
                   │  (frontend) │                        │  (frontend) │
                   └─────────────┘                        └─────────────┘
```

### 1.3 Technology Stack Versions

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend framework** | FastAPI | 0.115.0+ |
| **ASGI server** | Uvicorn | 0.30.0+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **PostgreSQL driver** | asyncpg | 0.29.0+ |
| **SQL Server driver** | pymssql | 2.3.0+ |
| **DB migrations** | Alembic | 1.13.0+ |
| **Scheduler** | APScheduler | 3.10.0+ |
| **Config management** | pydantic-settings | 2.0.0+ |
| **Password hashing** | bcrypt | 4.1.0+ |
| **JWT** | PyJWT | 2.8.0+ |
| **HTTP client** | httpx | 0.27.0+ |
| **Frontend framework** | Vue.js | 3.4.0+ |
| **Router** | Vue Router | 4.3.0+ |
| **Build tool** | Vite | 5.4.0+ |
| **HTTP client** | Axios | 1.7.0+ |
| **Chart library** | ECharts | 5.5.0+ |
| **Database** | PostgreSQL | 16 |
| **Containerization** | Docker | 20.10+ |
| **Orchestration** | Docker Compose | 2.0+ |
| **Web server** | Nginx | 1.26+ |

## 2. Project Structure

### 2.1 Backend Structure

```
backend/
├── alembic/                    # Database migration scripts
│   ├── versions/              # Migration version files
│   ├── env.py                 # Migration environment config
│   └── script.py.mako         # Migration script template
├── app/                        # Application code
│   ├── collectors/            # Data collectors
│   │   ├── __init__.py
│   │   ├── collector.py       # Collection coordinator
│   │   ├── sqlserver.py       # SQL Server connection management
│   │   ├── performance.py     # Performance metric collection
│   │   ├── deadlock.py        # Deadlock detection
│   │   ├── slow_query.py      # Slow query collection
│   │   ├── blocking.py        # Blocking process collection
│   │   ├── disk.py            # Disk space collection
│   │   └── index_analyzer.py  # Index analysis
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── performance.py     # Performance metric model
│   │   ├── deadlock.py        # Deadlock event model
│   │   ├── alert.py           # Alert log model
│   │   ├── alert_rule.py      # Alert rule model
│   │   ├── user.py            # User model
│   │   ├── instance.py        # Monitored instance model
│   │   ├── slow_query.py      # Slow query model
│   │   ├── blocking.py        # Blocking event model
│   │   ├── disk.py            # Disk space model
│   │   ├── index_analysis.py  # Index analysis model
│   │   ├── audit_log.py       # Audit log model
│   │   ├── config.py          # System config model
│   │   └── report.py          # Report record model
│   ├── routers/               # API routers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management endpoints
│   │   ├── metrics.py         # Performance metric endpoints
│   │   ├── deadlocks.py       # Deadlock endpoints
│   │   ├── alerts.py          # Alert endpoints
│   │   ├── alert_rules.py     # Alert rule endpoints
│   │   ├── instances.py       # Instance management endpoints
│   │   ├── slow_queries.py    # Slow query endpoints
│   │   ├── blocking.py        # Blocking endpoints
│   │   ├── disk.py            # Disk endpoints
│   │   ├── indexes.py         # Index endpoints
│   │   ├── audit_logs.py      # Audit log endpoints
│   │   ├── config.py          # Config endpoints
│   │   ├── export.py          # Data export endpoints
│   │   ├── notifications.py   # Notification endpoints
│   │   ├── reports.py         # Report endpoints
│   │   └── upgrade.py         # Online upgrade endpoints
│   ├── services/              # Business services
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication service
│   │   ├── alert_service.py   # Alert service
│   │   ├── audit_service.py   # Audit service
│   │   ├── notification.py    # Notification service
│   │   ├── deepseek.py        # AI analysis service
│   │   └── upgrade_service.py # Online upgrade service
│   ├── __init__.py
│   ├── config.py              # Config management
│   ├── database.py            # Database connection
│   ├── init_db.py             # Database initialization
│   ├── main.py                # Application entry point
│   └── scheduler.py           # Scheduled task management
├── .env.example               # Environment variable template
├── Dockerfile                 # Docker build file
├── alembic.ini                # Alembic config
└── requirements.txt           # Python dependencies
```

### 2.2 Frontend Structure

```
frontend/
├── src/
│   ├── api/                   # API client
│   │   └── index.js           # Axios instance and API functions
│   ├── components/            # Shared components
│   │   └── Layout.vue         # Layout component
│   ├── router/                # Router config
│   │   └── index.js           # Route definitions
│   ├── stores/                # State management
│   │   ├── auth.js            # Auth state
│   │   └── theme.js           # Theme state
│   ├── styles/                # Style files
│   │   └── theme.css          # Theme styles
│   ├── utils/                 # Utility functions
│   │   └── datetime.js        # Date/time utilities
│   ├── views/                 # Page components
│   │   ├── Dashboard.vue      # Dashboard
│   │   ├── Trends.vue         # Performance trends
│   │   ├── Deadlocks.vue      # Deadlock monitoring
│   │   ├── Alerts.vue         # Alert management
│   │   ├── AlertRules.vue     # Alert rules
│   │   ├── SlowQueries.vue    # Slow query analysis
│   │   ├── Blocking.vue       # Blocking processes
│   │   ├── Disk.vue           # Disk space
│   │   ├── Indexes.vue        # Index analysis
│   │   ├── Instances.vue      # Instance management
│   │   ├── Users.vue          # User management
│   │   ├── AuditLogs.vue      # Audit logs
│   │   ├── Settings.vue       # System settings
│   │   ├── Report.vue         # System reports
│   │   ├── Upgrade.vue        # Online upgrade
│   │   ├── Login.vue          # Login page
│   │   ├── ForgotPassword.vue  # Forgot password
│   │   ├── ResetPassword.vue   # Reset password (redirects to forgot password)
│   │   ├── Profile.vue         # Personal settings
│   │   └── Setup.vue           # Installation wizard
│   ├── App.vue                # Root component
│   └── main.js                # Application entry
├── Dockerfile                 # Docker build file
├── index.html                 # HTML entry
├── package.json               # Node.js dependencies
├── package-lock.json          # Dependency lock file
└── vite.config.js             # Vite config
```

## 3. Core Module Implementation

### 3.1 Data Collection Module

#### 3.1.1 Collection Coordinator (collector.py)

The collection coordinator is the core component of data collection, responsible for integrating multiple collectors:

```python
class MetricsCollector:
    """Metric collection coordinator"""
    
    def __init__(self, connection_manager: MSSQLConnectionManager = None):
        self.connection_manager = connection_manager or MSSQLConnectionManager()
        self.performance_collector = PerformanceCollector()
        self.deadlock_detector = DeadlockDetector()
        self.slow_query_collector = SlowQueryCollector()
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Run one full collection cycle"""
        result = {
            "metrics": [],
            "deadlocks": [],
            "slow_queries": [],
        }
        
        # Get connection
        connection = self.connection_manager.get_connection()
        
        # Collect performance metrics
        perf_metrics = self.performance_collector.collect_all(connection)
        # ... process performance metrics
        
        # Collect deadlock events
        deadlock_events = self.deadlock_detector.detect(connection)
        # ... process deadlock events
        
        # Collect slow queries
        slow_query_data = self.slow_query_collector.collect_slow_queries(connection)
        # ... process slow queries
        
        return result
```

#### 3.1.2 SQL Server Connection Management (sqlserver.py)

The connection manager is responsible for managing connections to SQL Server:

```python
class MSSQLConnectionManager:
    """SQL Server connection manager"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or settings.MSSQL_HOST
        self.port = port or settings.MSSQL_PORT
        self.user = user or settings.MSSQL_USER
        self.password = password or settings.MSSQL_PASSWORD
        self.database = database or settings.MSSQL_DATABASE
        self._connection = None
    
    def get_connection(self) -> pymssql.Connection:
        """Get SQL Server connection (with retry mechanism)"""
        if self._connection and self._test_connection_alive():
            return self._connection
        
        # Retry logic
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

#### 3.1.3 Performance Metric Collection (performance.py)

The performance collector gathers various metrics from SQL Server DMVs:

```python
class PerformanceCollector:
    """SQL Server performance metric collector"""
    
    def collect_cpu(self, connection) -> Dict[str, Any]:
        """Collect CPU usage"""
        # Query sys.dm_os_ring_buffers for CPU usage
        pass
    
    def collect_memory(self, connection) -> Dict[str, Any]:
        """Collect memory usage"""
        # Query sys.dm_os_performance_counters for memory metrics
        pass
    
    def collect_connections(self, connection) -> Dict[str, Any]:
        """Collect connection info"""
        # Query sys.dm_exec_sessions for connection counts
        pass
    
    def collect_io(self, connection) -> Dict[str, Any]:
        """Collect I/O statistics"""
        # Query sys.dm_io_virtual_file_stats for I/O metrics
        pass
```

#### 3.1.4 Deadlock Detection (deadlock.py)

The deadlock detector captures deadlock events from SQL Server system health sessions:

```python
class DeadlockDetector:
    """Deadlock event detector"""
    
    def detect(self, connection) -> List[Dict[str, Any]]:
        """Detect deadlock events"""
        # Query xml_deadlock_report in the system_health session
        # Parse deadlock XML and extract relevant info
        pass
```

### 3.2 Scheduled Task Management (scheduler.py)

The scheduler uses APScheduler to manage scheduled collection tasks:

```python
class SchedulerManager:
    """APScheduler manager"""
    
    def setup(self, app, settings: Settings):
        """Configure the scheduler"""
        self.scheduler = AsyncIOScheduler()
        self._alert_engine = AlertEngine(db_session_factory=async_session_factory)
        
        interval = settings.SCHEDULER_INTERVAL_SECONDS
        self.add_collect_job(interval_seconds=interval)
    
    async def _collect_and_store(self):
        """Collection task: iterate all active instances, collect metrics, write to PostgreSQL"""
        # Load runtime config
        runtime_config = await self._load_runtime_config()
        
        # Determine whether multi-instance mode is enabled
        instances_enabled = runtime_config.get("mssql_instances_enabled", "false").lower() == "true"
        
        if instances_enabled:
            await self._collect_multi_instance(runtime_config)
        else:
            await self._collect_single_instance(runtime_config)
    
    async def _collect_multi_instance(self, runtime_config):
        """Multi-instance collection mode"""
        instances = await self._load_active_instances()
        
        for instance in instances:
            # Create an independent connection manager for each instance
            conn_mgr = MSSQLConnectionManager.get_connection_for_instance(...)
            collector = MetricsCollector(connection_manager=conn_mgr)
            data = collector.collect_all_metrics()
            
            # Store data
            await self._store_metrics(session, data["metrics"], server_address)
            await self._store_deadlocks(session, data["deadlocks"], server_address)
            await self._store_slow_queries(session, data["slow_queries"], server_address)
        
        # Run alert checks
        await self._run_alert_checks(aggregated_data)
```

### 3.3 Alert Engine (alert_service.py)

The alert engine is responsible for checking alert rules and triggering alerts:

```python
class AlertEngine:
    """Alert rule engine"""
    
    def __init__(self, db_session_factory):
        self.session_factory = db_session_factory
        self.notification_service = NotificationService()
        
        # Built-in alert rules
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
        """Run the full alert flow"""
        # 1. Check built-in rules
        triggered = await self.check_rules(metrics_data)
        
        # 2. Load and check custom rules
        custom_triggered = await self._check_custom_rules(metrics_data)
        triggered.extend(custom_triggered)
        
        # 3. Check cooldown → create alert
        for alert_type, severity, message in triggered:
            cooldown = self._get_cooldown_minutes(alert_type)
            if await self._is_in_cooldown(alert_type, cooldown):
                continue
            alert = await self.create_alert(alert_type, severity, message)
        
        return created_alerts
```

### 3.4 Notification Service (notification.py)

The notification service supports multiple notification channels:

```python
class NotificationService:
    """Composite notification service"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.dingtalk_notifier = DingTalkNotifier()
        self.wecom_notifier = WeComNotifier()
        self.feishu_notifier = FeishuNotifier()
        self.feishu_app_notifier = FeishuAppNotifier()
    
    async def notify_all(self, subject: str, body: str) -> Dict[str, bool]:
        """Send notifications through all channels simultaneously"""
        result = {
            "email": False,
            "dingtalk": False,
            "wecom": False,
            "feishu": False,
            "feishu_app": False,
        }
        
        # Email sent synchronously
        result["email"] = self.email_notifier.send(subject, body)
        
        # DingTalk sent asynchronously
        result["dingtalk"] = await self.dingtalk_notifier.send(body)
        
        # WeCom sent asynchronously
        result["wecom"] = await self.wecom_notifier.send(body)
        
        # Feishu webhook sent asynchronously
        result["feishu"] = await self.feishu_notifier.send(body)
        
        # Feishu app notification: triggered only for critical errors; recipients support open_id or email address
        result["feishu_app"] = await self.feishu_app_notifier.send(body)
        
        return result
```

### 3.5 Authentication Service (auth_service.py)

The authentication service provides JWT authentication and permission control:

```python
class AuthService:
    """Authentication service"""
    
    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    
    @staticmethod
    def create_access_token(user_id: int, username: str, role: str) -> str:
        """Generate JWT access token"""
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
        """Decode JWT token"""
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

#### Password Reset Verification Code

Password reset uses a verification code stored in memory (expires in 30 minutes):

```python
def generate_reset_code(user_id: int) -> str:
    """Generate a 6-digit verification code"""
    code = "".join(random.choices(string.digits, k=6))
    _PASSWORD_RESET_CODES[code] = {
        "user_id": user_id,
        "expires_at": now + timedelta(minutes=30),
    }
    return code

def verify_reset_code(code: str) -> Optional[int]:
    """Verify the code and return user_id"""
    data = _PASSWORD_RESET_CODES.get(code)
    if not data or datetime.now(timezone.utc) > data["expires_at"]:
        return None
    return data["user_id"]
```

The code is invalidated immediately after use; regenerating for the same user clears the old code.

### 3.6 AI Analysis Service (deepseek.py)

The AI analysis service integrates the DeepSeek API for intelligent analysis:

```python
async def analyze_deadlock(deadlock_info: dict) -> Optional[str]:
    """Analyze deadlock using DeepSeek AI"""
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
                        "content": "You are a senior SQL Server database performance optimization expert...",
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

## 4. Database Design

### 4.1 ER Diagram

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │  system_configs │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ username        │       │ config_key      │
│ password_hash   │       │ config_value    │
│ role            │       │ description     │
│ full_name       │       │ created_at      │
│ email           │       │ updated_at      │
│ is_active       │       └─────────────────┘
│ last_login_at   │
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

### 4.2 Index Design

```sql
-- Performance metrics table indexes
CREATE INDEX idx_metrics_collected_at ON metrics(collected_at);
CREATE INDEX idx_metrics_category ON metrics(category);
CREATE INDEX idx_metrics_server_address ON metrics(server_address);
CREATE INDEX idx_metrics_category_name_collected ON metrics(category, metric_name, collected_at);

-- Deadlock events table indexes
CREATE INDEX idx_deadlocks_occur_at ON deadlocks(occur_at);
CREATE INDEX idx_deadlocks_server_address ON deadlocks(server_address);

-- Alert logs table indexes
CREATE INDEX idx_alert_logs_triggered_at ON alert_logs(triggered_at);
CREATE INDEX idx_alert_logs_alert_type ON alert_logs(alert_type);
CREATE INDEX idx_alert_logs_severity ON alert_logs(severity);

-- Slow queries table indexes
CREATE INDEX idx_slow_queries_collected_at ON slow_queries(collected_at);
CREATE INDEX idx_slow_queries_server_address ON slow_queries(server_address);
CREATE INDEX idx_slow_queries_sql_hash ON slow_queries(sql_hash);

-- Users table indexes
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Monitored instances table indexes
CREATE INDEX idx_monitored_instances_is_active ON monitored_instances(is_active);
CREATE INDEX idx_monitored_instances_is_connected ON monitored_instances(is_connected);

-- Audit logs table indexes
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

## 5. API Design

### 5.1 RESTful API Conventions

- Standard HTTP methods: GET, POST, PUT, DELETE
- JSON format for data exchange
- HTTP status codes indicate request results
- JWT for authentication
- All APIs are prefixed with `/api`

### 5.2 Authentication Flow

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │                    │ Database │
└────┬─────┘                    └────┬─────┘                    └────┬─────┘
     │                               │                               │
     │  1. POST /api/auth/login      │                               │
     │  {username, password}         │                               │
     │──────────────────────────────▶│                               │
     │                               │  2. Query user               │
     │                               │──────────────────────────────▶│
     │                               │  3. Return user info         │
     │                               │◀──────────────────────────────│
     │                               │                               │
     │                               │  4. Verify password          │
     │                               │  5. Generate JWT             │
     │                               │                               │
     │  6. Return {access_token, user}│                              │
     │◀──────────────────────────────│                               │
     │                               │                               │
     │  7. GET /api/metrics/realtime │                               │
     │  Authorization: Bearer <token>│                               │
     │──────────────────────────────▶│                               │
     │                               │  8. Verify JWT               │
     │                               │  9. Query data               │
     │                               │──────────────────────────────▶│
     │                               │  10. Return data             │
     │                               │◀──────────────────────────────│
     │  11. Return metrics data      │                               │
     │◀──────────────────────────────│                               │
     │                               │                               │
```

### 5.3 Detailed API Endpoints

#### 5.3.1 Authentication Endpoints

**POST /api/auth/login**
- Description: User login
- Request body:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- Response:
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
- Description: Get current user info
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string",
    "full_name": "string",
    "email": "string",
    "is_active": true,
    "last_login_at": "2024-01-01T00:00:00Z"
  }
  ```

**POST /api/auth/change_password**
- Description: Change password
- Request header: `Authorization: Bearer <token>`
- Request body:
  ```json
  {
    "old_password": "string",
    "new_password": "string"
  }
  ```
- Response:
  ```json
  {
    "message": "Password changed successfully"
  }
  ```

**POST /api/auth/forgot_password**
- Description: Request password reset verification code
- Request body:
  ```json
  { "email": "string" }
  ```
- Response:
  ```json
  { "message": "If the email is registered, you will receive a verification code" }
  ```

**POST /api/auth/reset_password**
- Description: Reset password with verification code
- Request body:
  ```json
  {
    "email": "string",
    "code": "6-digit verification code",
    "new_password": "string"
  }
  ```
- Response:
  ```json
  { "message": "Password reset successfully" }
  ```

**PUT /api/auth/me**
- Description: Update current user profile (name, email)
- Request header: `Authorization: Bearer <token>`
- Request body:
  ```json
  {
    "full_name": "string",
    "email": "string"
  }
  ```
- Response: Returns updated user info

#### 5.3.2 Performance Metric Endpoints

**GET /api/metrics/realtime**
- Description: Get real-time metrics
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get historical metrics
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `category` (required): metric category
  - `metric_name` (optional): metric name
  - `start_time` (required): start time
  - `end_time` (required): end time
  - `limit` (optional): max records, default 1000
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get metric summary
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `server_address` (optional): filter by instance
- Response:
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

#### 5.3.3 Deadlock Endpoints

**GET /api/deadlocks**
- Description: Get deadlock list
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `limit` (optional): max records
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get deadlock details
- Request header: `Authorization: Bearer <token>`
- Response:
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
- Description: AI analysis of deadlock
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "analysis_result": "..."
  }
  ```

#### 5.3.4 Alert Endpoints

**GET /api/alerts**
- Description: Get alert list
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `severity` (optional): severity level
  - `limit` (optional): max records
- Response:
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
- Description: Acknowledge alert
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Alert acknowledged"
  }
  ```

#### 5.3.5 Alert Rule Endpoints

**GET /api/alert-rules**
- Description: Get alert rule list
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  [
    {
      "id": 1,
      "name": "High memory usage",
      "description": "Alert when memory usage exceeds 85%",
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
- Description: Create alert rule
- Request header: `Authorization: Bearer <token>`
- Request body:
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
- Response:
  ```json
  {
    "id": 1,
    "name": "string",
    ...
  }
  ```

**PUT /api/alert-rules/{id}**
- Description: Update alert rule
- Request header: `Authorization: Bearer <token>`
- Request body: same as create
- Response: same as create

**DELETE /api/alert-rules/{id}**
- Description: Delete alert rule
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Alert rule deleted"
  }
  ```

**PUT /api/alert-rules/{id}/toggle**
- Description: Enable/disable alert rule
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "id": 1,
    "enabled": true
  }
  ```

#### 5.3.6 Instance Management Endpoints

**GET /api/instances**
- Description: Get instance list
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  [
    {
      "id": 1,
      "name": "Production",
      "host": "10.0.0.1",
      "port": 1433,
      "username": "sa",
      "database_name": "master",
      "is_active": true,
      "is_connected": true,
      "last_connected_at": "2024-01-01T00:00:00Z",
      "last_disconnected_at": null,
      "connection_error": null,
      "description": "Production SQL Server"
    }
  ]
  ```

**POST /api/instances**
- Description: Create instance
- Request header: `Authorization: Bearer <token>`
- Request body:
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
- Response: same as a single object in the instance list

**PUT /api/instances/{id}**
- Description: Update instance
- Request header: `Authorization: Bearer <token>`
- Request body: same as create
- Response: same as create

**DELETE /api/instances/{id}**
- Description: Delete instance
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Instance deleted"
  }
  ```

**POST /api/instances/{id}/test**
- Description: Test instance connection
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "success": true,
    "message": "Connection successful"
  }
  ```

#### 5.3.7 Slow Query Endpoints

**GET /api/slow-queries**
- Description: Get slow query list
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `limit` (optional): max records
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get slow query statistics
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `server_address` (optional): filter by instance
- Response:
  ```json
  {
    "total_count": 100,
    "avg_duration_ms": 150,
    "max_duration_ms": 5000,
    "top_queries": [...]
  }
  ```

#### 5.3.8 Blocking Endpoints

**GET /api/blocking/realtime**
- Description: Get real-time blocking
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get blocking history
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `limit` (optional): max records
  - `server_address` (optional): filter by instance
- Response: same as real-time blocking

#### 5.3.9 Disk Endpoints

**GET /api/disk/space**
- Description: Get disk space
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get disk history
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `database_name` (optional): database name
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `server_address` (optional): filter by instance
- Response: same as disk space

#### 5.3.10 Index Endpoints

**GET /api/indexes/missing**
- Description: Get missing indexes
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `limit` (optional): max records
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Get index fragmentation
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `database_name` (optional): database name
  - `threshold` (optional): fragmentation threshold
  - `limit` (optional): max records
  - `server_address` (optional): filter by instance
- Response:
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

#### 5.3.11 Audit Log Endpoints

**GET /api/audit-logs**
- Description: Get audit logs
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `user_id` (optional): user ID
  - `action` (optional): operation type
  - `limit` (optional): max records
- Response:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin",
      "action": "login",
      "detail": "User logged in successfully",
      "ip_address": "192.168.1.1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
  ```

#### 5.3.12 Data Export Endpoints

**GET /api/export/metrics**
- Description: Export metrics data
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (required): start time
  - `end_time` (required): end time
  - `category` (optional): metric category
  - `server_address` (optional): filter by instance
- Response: CSV file

**GET /api/export/alerts**
- Description: Export alert data
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (required): start time
  - `end_time` (required): end time
  - `severity` (optional): severity level
- Response: CSV file

**GET /api/export/deadlocks**
- Description: Export deadlock data
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (required): start time
  - `end_time` (required): end time
  - `server_address` (optional): filter by instance
- Response: CSV file

**GET /api/export/slow-queries**
- Description: Export slow query data
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (required): start time
  - `end_time` (required): end time
  - `server_address` (optional): filter by instance
- Response: CSV file

#### 5.3.13 Notification Endpoints

**GET /api/notifications**
- Description: Get notification list
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `limit` (optional): max records, default 20
- Response:
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
- Description: Mark notification as read
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Notification marked as read"
  }
  ```

**DELETE /api/notifications/{id}**
- Description: Delete notification
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Notification deleted"
  }
  ```

**POST /api/notifications/read-all**
- Description: Mark all notifications as read
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "All notifications marked as read"
  }
  ```

#### 5.3.14 Report Endpoints

**GET /api/reports/summary**
- Description: Get report summary
- Request header: `Authorization: Bearer <token>`
- Query parameters:
  - `start_time` (optional): start time
  - `end_time` (optional): end time
  - `server_address` (optional): filter by instance
- Response:
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
- Description: Save report
- Request header: `Authorization: Bearer <token>`
- Request body:
  ```json
  {
    "title": "string",
    "content": "string",
    "report_data": {},
    "ai_analysis": "string"
  }
  ```
- Response:
  ```json
  {
    "id": 1,
    "title": "string",
    ...
  }
  ```

**GET /api/reports/history**
- Description: Get report history
- Request header: `Authorization: Bearer <token>`
- Response:
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
- Description: Delete report
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "message": "Report deleted"
  }
  ```

#### 5.3.15 Config Endpoints

**GET /api/config**
- Description: Get all config
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  [
    {
      "id": 1,
      "config_key": "mssql_host",
      "config_value": "10.0.0.1",
      "description": "SQL Server server address"
    }
  ]
  ```

**GET /api/config/{key}**
- Description: Get single config
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "id": 1,
    "config_key": "mssql_host",
    "config_value": "10.0.0.1",
    "description": "SQL Server server address"
  }
  ```

**PUT /api/config/{key}**
- Description: Update config
- Request header: `Authorization: Bearer <token>`
- Request body:
  ```json
  {
    "config_value": "string"
  }
  ```
- Response:
  ```json
  {
    "id": 1,
    "config_key": "mssql_host",
    "config_value": "10.0.0.2",
    "description": "SQL Server server address"
  }
  ```

#### 5.3.16 Version Check Endpoint

**GET /api/version/check**
- Description: Check whether a new version is available, comparing the local version with the latest GitHub version
- Request header: `Authorization: Bearer <token>`
- Response:
  ```json
  {
    "current_version": "1.0.11",
    "latest_version": "1.1.0",
    "has_update": true,
    "github_url": "https://github.com/qianhui602/SQL_MONITORING_TOOLS",
    "message": "New version v1.1.0 found, current version v1.0.11. Upgrade recommended for the latest features and security fixes."
  }
  ```

## 6. Frontend Architecture

### 6.1 Component Structure

```
App.vue
└── Layout.vue
    ├── Sidebar
    │   ├── Logo
    │   ├── Navigation Menu
    │   ├── Collapse Button
    │   └── Version Display (version + update indicator)
    ├── Topbar
    │   ├── Page Title
    │   ├── Notification Bell
    │   ├── Theme Toggle
    │   └── User Menu
    ├── TabBar (multi-tab navigation)
    │   ├── Tab Items (closable tabs)
    │   ├── Close Others Button
    │   └── Context Menu (right-click menu)
    ├── Update Banner (version update banner)
    └── Main Content
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
        ├── Help.vue
        ├── Login.vue
        ├── Profile.vue
        ├── ForgotPassword.vue
        ├── ResetPassword.vue
        └── Setup.vue
```

### 6.2 Router Configuration

```javascript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login', public: true, layout: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard', icon: 'dashboard' }
  },
  // ... other routes
]

// Route guard
router.beforeEach((to, from, next) => {
  const isPublic = to.meta?.public
  const authed = authStore.isAuthenticated.value

  // Redirect unauthenticated users to the login page
  if (!isPublic && !authed) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // Redirect non-admin users away from admin-only pages
  if (to.meta?.requiresAdmin && !authStore.isAdmin.value) {
    return next({ path: '/dashboard' })
  }

  // Redirect logged-in users away from the login page
  if (to.path === '/login' && authed) {
    return next({ path: '/dashboard' })
  }

  next()
})
```

### 6.3 State Management

Uses Vue 3 reactive APIs for state management:

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
      super_admin: 'Super Admin',
      admin: 'Admin',
      viewer: 'Read-only User'
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

### 6.4 API Client

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

// Request interceptor: attach JWT token
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

// Response interceptor: handle 401 errors
// Public path whitelist: /login, /forgot-password, /reset-password, /setup
// 401 on public pages no longer forces a redirect to the login page
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      const publicPaths = ['/login', '/forgot-password', '/reset-password', '/setup']
      const isPublicPath = publicPaths.some((p) => window.location.pathname.startsWith(p))
      if (!isPublicPath) {
        clearAuth()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API functions
export function getRealtimeMetrics() {
  return request.get('/metrics/realtime')
}

export function getHistoryMetrics(params) {
  return request.get('/metrics/history', { params })
}

// ... other API functions
```

### 6.5 Chart Components

Uses ECharts for data visualization:

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
    data: ['CPU Usage', 'Memory Usage']
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
      name: 'CPU Usage',
      type: 'line',
      data: []
    },
    {
      name: 'Memory Usage',
      type: 'line',
      data: []
    }
  ]
})
</script>
```

## 7. Deployment Architecture

### 7.1 Docker Compose Deployment

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

### 7.2 Backend Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    freetds-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libct4 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.3 Frontend Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:1.26-alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 7.4 Nginx Configuration

```nginx
server {
    listen 80;
    server_name localhost;

    # Static files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 8. Performance Optimization

### 8.1 Backend Optimization

1. **Async processing**: use FastAPI's async features to improve concurrency
2. **Connection pooling**: use SQLAlchemy's connection pool to reduce DB connection overhead
3. **Caching**: cache frequently queried data
4. **Batch operations**: use batch inserts to reduce DB interactions
5. **Index optimization**: ensure tables have appropriate indexes

### 8.2 Frontend Optimization

1. **Code splitting**: use Vite's code splitting to load components on demand
2. **Image optimization**: use appropriate image formats and compression
3. **Caching**: leverage browser caching to reduce requests
4. **Lazy loading**: lazy-load non-first-screen components
5. **Virtual scrolling**: use virtual scrolling for large data lists

### 8.3 Database Optimization

1. **Index optimization**:
   - Create indexes for frequently queried fields
   - Use composite indexes for multi-field queries
   - Regularly analyze index usage

2. **Query optimization**:
   - Use EXPLAIN ANALYZE to analyze query plans
   - Avoid SELECT *, only query needed fields
   - Use LIMIT to cap returned records

3. **Data cleanup**:
   - Regularly clean historical data
   - Use partitioned tables for large data volumes

## 9. Security Design

### 9.1 Authentication Security

1. **Password encryption**: passwords stored encrypted with bcrypt
2. **JWT tokens**: JWT for authentication
3. **Token expiration**: reasonable token expiration times
4. **HTTPS**: use HTTPS in production

### 9.2 API Security

1. **Permission control**: role-based access control
2. **Input validation**: use Pydantic for input validation
3. **SQL injection protection**: use parameterized queries
4. **XSS protection**: escape output

### 9.3 Data Security

1. **Sensitive info encryption**: encrypt sensitive configuration at rest
2. **Access control**: restrict database access permissions
3. **Audit logs**: record all critical operations
4. **Data backup**: regularly back up data

## 10. Monitoring & Operations

### 10.1 Health Check

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": settings.PROJECT_NAME}
```

### 10.2 Logging Configuration

```python
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
```

### 10.3 Performance Monitoring

1. **Request latency**: monitor API request latency
2. **Error rate**: monitor API error rate
3. **Database connections**: monitor connection pool usage
4. **System resources**: monitor CPU, memory, and disk usage

### 10.4 Alert Configuration

1. **Service outage**: monitor whether services are running
2. **Performance degradation**: monitor API response times
3. **Error spikes**: monitor error logs
4. **Resource exhaustion**: monitor system resource usage

## 11. Testing Strategy

### 11.1 Unit Tests

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

### 11.2 Integration Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_metrics_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first to get a token
        login_response = await client.post("/api/auth/login", json={
            "username": "Admin",
            "password": "Chuz0001"
        })
        token = login_response.json()["access_token"]
        
        # Test getting real-time metrics
        response = await client.get(
            "/api/metrics/realtime",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

### 11.3 End-to-End Tests

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

## 12. FAQ

### 12.1 Connection Issues

**Q: Cannot connect to SQL Server**
A: Check the following:
1. Whether SQL Server allows remote connections
2. Whether the firewall allows port 1433
3. Whether TCP/IP protocol is enabled for SQL Server
4. Whether username and password are correct

**Q: Cannot connect to PostgreSQL**
A: Check the following:
1. Whether PostgreSQL allows remote connections
2. Whether the firewall allows port 5432
3. Whether pg_hba.conf allows connections
4. Whether username and password are correct

### 12.2 Performance Issues

**Q: What collection interval should I set**
A: Depends on actual needs:
- Production: 60-300 seconds
- Testing: 10-60 seconds
- Development: 5-10 seconds

**Q: How long should historical data be retained**
A: Recommendations:
- Performance metrics: 30-90 days
- Deadlock events: 90-180 days
- Alert logs: 90-180 days
- Audit logs: 180-365 days

### 12.3 Alert Issues

**Q: Alerts are not triggering**
A: Check the following:
1. Whether the alert rule is enabled
2. Whether the alert threshold is reasonable
3. Whether you are in a silent period
4. Whether you are in a cooldown period

**Q: Alert notifications are not being sent**
A: Check the following:
1. Whether notification channels are configured correctly
2. Whether the SMTP server is working
3. Whether DingTalk/WeCom webhooks are valid
4. Whether the network is normal

## 13. Version History

### v1.0.0 (2024-01-01)
- Initial release
- Basic monitoring features
- Alert management
- User management

### v1.1.0 (2024-02-01)
- Added slow query analysis
- Added blocking process monitoring
- Added disk space monitoring
- Added index analysis

### v1.2.0 (2024-03-01)
- Added multi-instance monitoring support
- Added AI analysis
- Added report generation
- Improved performance and stability

### v1.3.0 (2024-04-01)
- Added WeCom notification support
- Added data export
- Added audit logs
- Improved user experience

### v1.4.0 (2026-01-01)
- Added password recovery (email verification code)
- Added personal settings page (change name, email)
- Added installation wizard (first-deployment guide)
- Added notification sound alerts
- Added brand customization (custom title and logo)
- Added frontend access URL config
- Optimization: 401 on public pages no longer forces login redirect

### v1.5.0 (2026-07-09)
- Added SQL disconnection monitoring
  - Active ping to detect connection health before collection
  - Automatic alerts on disconnect/recovery
  - Connection status fields added to monitored_instances table
- Added Dashboard database connection status display
  - Shows online/offline status of all instances
  - Breathing-light animation for online status
- Added multi-tab navigation bar (Dify-inspired)
  - Auto-creates tabs, click to switch, closable
  - Right-click menu: close current/others/all
- Added Help Center page (/help)
  - Left TOC navigation + search filter
  - Usage instructions for all modules and FAQ
- Added version detection and upgrade reminders
  - Auto-compare local with latest GitHub version
  - Update indicator dot on sidebar version number
  - Upgrade notification banner at the bottom
- UI improvements
  - Dashboard stat cards with colorful gradient icons
  - Show/hide customization for stat cards
  - Login page UI overhaul (glassmorphism)
  - Removed acknowledge button on alert management page
  - Responsive layout optimization
- Documentation updates
  - README with upgrade guide and one-click upgrade scripts
  - Added user manual (Docs/USER_MANUAL.md)

### v1.6.0 (2026-08-26)
- Added critical-error Feishu app notifications
  - Reaches designated users directly via Feishu custom app (tenant_access_token + im/v1/messages)
  - Recipients support both open_id and email address with receive_id_type auto-detection
  - tenant_access_token cached at class level (valid ~2 hours, refreshed 5 minutes early)
  - Triggered only for critical-severity alerts, independent of the group robot webhook channel
- Added Feishu group robot webhook notification channel
- Send failures now classify exception types and surface specific reasons (connection failure / timeout / HTTP error / Feishu business code)
- System Settings "Notification Service" redesigned as card grid + modal config, each channel supports sending test messages
- Sidebar layout fix: page scrolling allowed and sidebar pinned via sticky positioning; all menus visible without zooming out on low-resolution screens

## 14. Future Plans

### 14.1 Feature Expansion
1. **More database support**: MySQL, Oracle, etc.
2. **Richer charts**: more chart types
3. **Smarter alerts**: machine-learning-based anomaly detection
4. **Better reports**: custom report templates

### 14.2 Performance Optimization
1. **Data compression**: compressed storage for historical data
2. **Sharding**: support for large data volumes
3. **Read/write splitting**: database read/write separation
4. **Cache optimization**: introduce Redis caching

### 14.3 Operations Optimization
1. **Automated deployment**: CI/CD support
2. **Container orchestration**: Kubernetes deployment
3. **Monitoring & alerting**: complete operations monitoring
4. **Log analysis**: ELK-based log analysis

