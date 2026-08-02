# SQL Monitoring Platform - Project Documentation

[简体中文](../PROJECT_DOCUMENTATION.md) | **English**

## 1. Project Overview

### 1.1 Introduction
The SQL Monitoring Platform is an MS SQL Server performance monitoring and alerting platform built with FastAPI + Vue.js + PostgreSQL. It provides real-time monitoring, historical trend analysis, alert management, deadlock detection, and slow query analysis, helping database administrators and developers fully understand the running state of SQL Server.

### 1.2 Project Goals
- Real-time monitoring of key SQL Server performance metrics (CPU, memory, connections, I/O, etc.)
- Automatic detection and analysis of deadlock events
- Identification and analysis of slow queries
- Flexible alert rule configuration with multi-channel notifications
- Unified monitoring of multiple SQL Server instances
- Intuitive data visualization and reporting

### 1.3 Key Features

#### 1.3.1 Performance Monitoring
- **Real-time metric monitoring**: CPU usage, memory usage, active connections, cache hit ratio, page life expectancy, etc.
- **Historical trend analysis**: Query historical metric data by time range with comparison analysis
- **Overview dashboard**: Summary of key performance metrics

#### 1.3.2 SQL Disconnection Monitoring
- **Connection status detection**: Actively pings SQL Server connectivity on every collection cycle
- **Status recording**: Records `is_connected`, `last_connected_at`, `last_disconnected_at`, and `connection_error` fields in the `monitored_instances` table
- **Automatic alerts**: Triggers a `connection_lost` critical alert on disconnection and a `connection_recovered` notification on recovery
- **Frontend display**: The Dashboard page shows online/offline status for all instances; the instance management page shows detailed connection info

#### 1.3.3 Deadlock Monitoring
- **Automatic detection**: Captures deadlock events via SQL Server system health sessions
- **Detailed analysis**: Records deadlock XML, victim session, involved SQL statements and objects
- **AI analysis**: Integrated with DeepSeek AI for intelligent deadlock analysis and optimization recommendations

#### 1.3.4 Slow Query Analysis
- **Automatic collection**: Identifies queries with excessive execution time via DMVs
- **Statistical analysis**: Provides execution count, CPU consumption, logical reads, etc. for slow queries
- **SQL text recording**: Full SQL text of slow queries is recorded

#### 1.3.5 Alert Management
- **Built-in rules**: High memory usage, deadlock detection, collection interruption, connection lost/recovered, etc.
- **Custom rules**: Users can define custom alert rules including metrics, thresholds, operators, etc.
- **Cooldown control**: Prevents the same alert from repeatedly triggering in a short period
- **Silent periods**: Support configuring silent time windows for alerts

#### 1.3.6 Notification Service
- **Email notifications**: Send alert emails via SMTP
- **DingTalk notifications**: Support DingTalk robot webhook notifications
- **WeCom notifications**: Support WeCom (WeChat Work) group robot webhook notifications
- **Multi-channel combination**: Support sending notifications through multiple channels simultaneously

#### 1.3.7 Blocking Process Monitoring
- **Real-time blocking detection**: Detects currently blocked processes
- **Historical records**: Records historical blocking event data

#### 1.3.8 Disk Space Monitoring
- **Space usage**: Monitors disk space usage of database files
- **Historical trends**: Provides historical disk space usage trends

#### 1.3.9 Index Analysis
- **Missing index detection**: Identifies missing indexes suggested by SQL Server
- **Index fragmentation analysis**: Analyzes the fragmentation level of indexes
- **Optimization recommendations**: Provides index optimization suggestions

#### 1.3.10 Instance Management
- **Multi-instance support**: Monitor multiple SQL Server instances simultaneously
- **Independent configuration**: Each instance can be configured with independent connection info
- **Connection testing**: Test whether an instance connection is healthy
- **Connection status display**: Real-time display of each instance's online/offline status, last connection time, and error messages

#### 1.3.11 User & Permission Management
- **Role permissions**: Super Admin, Admin, and Read-only User roles
- **User management**: CRUD operations for users
- **Password management**: Change passwords, stored encrypted with bcrypt
- **Password recovery**: Reset passwords via email verification codes without admin intervention
- **Personal settings**: Regular users can update their name, email, and other personal info

#### 1.3.12 Help Center
- **Help page**: Help center page accessible to all users (/help)
- **Table of contents navigation**: Left-side TOC navigation with scroll-highlighted current section
- **Content search**: Top search box filters help content in real time
- **Module documentation**: Usage instructions and operation guides for all feature modules
- **FAQ**: Includes FAQ and contact information

#### 1.3.13 Audit Logs
- **Operation records**: Records key user operations
- **Log queries**: Query audit logs by time, user, and operation type

#### 1.3.14 Reporting
- **Report generation**: Generates performance analysis reports based on monitoring data
- **AI analysis**: Integrated with DeepSeek AI for intelligent report analysis
- **Historical reports**: Save and view historical reports

#### 1.3.15 Data Export
- **Multi-format support**: Export to CSV, Excel, and other formats
- **Multiple data types**: Export metrics, alerts, deadlocks, slow queries, etc.

#### 1.3.16 Version Detection & Upgrade Reminder
- **Version detection**: Automatically compares local version with the latest GitHub version
- **Upgrade indicator**: Yellow dot next to the version number in the sidebar indicates a new version
- **Upgrade banner**: Upgrade notification banner at the bottom with a link to the upgrade guide
- **Upgrade guide**: README provides Docker and local development upgrade steps, including one-click upgrade scripts

### 1.4 User Roles

| Role | Description |
|------|-------------|
| **Super Admin (super_admin)** | Has all permissions, cannot be deleted, highest system privileges |
| **Admin (admin)** | Can manage users, modify config, view all data |
| **Read-only User (viewer)** | Can only view data, cannot modify config or manage users |

### 1.5 System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Vue.js Frontend│────▶│  FastAPI Backend│────▶│   PostgreSQL    │
│   (Nginx)       │     │   (Uvicorn)     │     │   (Storage)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   SQL Server    │
                        │ (Monitored Target)
                        └─────────────────┘
```

## 2. Feature Module Details

### 2.1 Dashboard
The dashboard is the system home page and provides:
- **Key metric cards**: CPU usage, memory usage, active connections, cache hit ratio, disk usage, batch requests/sec, lock waits, deadlock events, database instance count (9 cards total)
- **Card customization**: Drag-and-drop reordering and show/hide for statistic cards
- **Database connection status**: Real-time online/offline status of all instances with breathing-light animation
- **Deadlock event statistics**: Deadlock event count and latest deadlock time
- **Performance trend charts**: View historical trends by time range, with comparison modes (yesterday, last week, last month)
- **Custom charts**: Customize which charts are shown and their order

### 2.2 Performance Trends
Detailed historical trend analysis of performance metrics:
- View trends by metric category (CPU, memory, connection, I/O)
- Custom time ranges
- Multi-metric comparison analysis

### 2.3 Deadlocks
Detailed viewing and analysis of deadlock events:
- Deadlock event list: shows time, victim session, involved objects
- Deadlock details: view deadlock XML and participating sessions' SQL
- AI analysis: one-click DeepSeek AI analysis for optimization recommendations

### 2.4 Slow Queries
Slow query identification and analysis:
- Slow query list: shows SQL hash, execution count, total CPU time, average duration, etc.
- Statistical analysis: summary statistics of slow queries
- SQL text viewer: view the full SQL statement

### 2.5 Blocking
Real-time and historical monitoring of blocking processes:
- Real-time blocking: shows currently blocked processes
- Historical records: view historical blocking events

### 2.6 Disk
Disk space usage monitoring:
- Space usage: shows disk usage percentage of database files
- Historical trends: view historical disk space changes

### 2.7 Indexes
Index optimization recommendations:
- Missing indexes: shows missing indexes suggested by SQL Server
- Index fragmentation: analyzes index fragmentation levels

### 2.8 Alerts
Alert event viewing and handling:
- Alert list: shows alert type, severity, trigger time, message content
- Alert acknowledgment: support acknowledging alert events
- Notification status: shows whether notifications were sent

### 2.9 Alert Rules
Alert rule configuration management:
- Rule list: shows all alert rules
- Rule creation: create custom alert rules
- Rule editing: edit existing rules
- Enable/disable: enable or disable rules
- Silent periods: configure silent time windows for rules

### 2.10 Instances
SQL Server instance management:
- Instance list: shows all monitored instances
- Instance creation: add new monitored instances
- Instance editing: edit instance configurations
- Connection testing: test instance connectivity

### 2.11 Users
System user management:
- User list: shows all users
- User creation: create new users
- User editing: edit user information
- User deletion: delete users (super admin cannot be deleted)
- **Personal settings**: Users can update their own name and email (no admin permission needed)

### 2.12 Audit Logs
System operation log viewing:
- Log list: shows operation time, user, operation type, details
- Log queries: filter logs by conditions

### 2.13 Settings
System configuration management:
- Database connection configuration
- Collection interval configuration
- Alert threshold configuration
- Notification channel configuration
- Frontend access URL configuration (for links in password reset emails, etc.)
- Brand customization (system title, logo)
- Sound alert toggle

### 2.14 Reports
Performance analysis report generation and viewing:
- Report generation: generate reports from current monitoring data
- AI analysis: integrated with DeepSeek AI for intelligent analysis
- Report history: save and view historical reports
- Report export: export to PDF format

### 2.15 Forgot Password
Password reset flow:
- **Send verification code**: User enters registered email; system sends a 6-digit code (valid for 30 minutes)
- **Reset password**: User enters the code and new password to complete reset
- **Security mechanism**: Two-way validation between code and email to prevent unauthorized resets

### 2.16 Profile
Personal information management:
- **Basic info**: View username and role (read-only)
- **Edit info**: Change name and email
- **Change password**: Verify current password before setting a new one

## 3. Technology Stack

### 3.1 Backend
- **Python 3.12+**: Primary programming language
- **FastAPI**: Web framework providing high-performance async APIs
- **Uvicorn**: ASGI server
- **SQLAlchemy 2.0**: ORM framework with async support
- **asyncpg**: PostgreSQL async driver
- **pymssql**: SQL Server connection driver
- **Alembic**: Database migration tool
- **APScheduler**: Scheduled task management
- **Pydantic**: Data validation and configuration management
- **bcrypt**: Password hashing
- **PyJWT**: JWT token generation and validation
- **httpx**: Async HTTP client (for notifications and AI calls)

### 3.2 Frontend
- **Vue.js 3**: Frontend framework
- **Vue Router 4**: Routing
- **Vite 5**: Build tool
- **Axios**: HTTP client
- **ECharts 5**: Data visualization chart library
- **vue-echarts**: ECharts component for Vue.js
- **html2canvas**: HTML to image
- **jsPDF**: PDF generation

### 3.3 Database
- **PostgreSQL 16**: Primary database, stores monitoring data and configuration
- **SQL Server**: Monitored target database

### 3.4 Deployment
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Frontend static file serving and reverse proxy

### 3.5 AI Integration
- **DeepSeek AI**: AI service for deadlock analysis and report generation

## 4. System Configuration

### 4.1 Environment Variables

| Config | Description | Default |
|--------|-------------|---------|
| **Project Basics** | | |
| `PROJECT_NAME` | Project name | SQL 监控平台 |
| `DEBUG` | Debug mode toggle | false |
| `CORS_ORIGINS` | Allowed CORS origins | ["http://localhost:3000"] |
| **PostgreSQL** | | |
| `PG_HOST` | Database host | postgres |
| `PG_PORT` | Database port | 5432 |
| `PG_USER` | Database user | postgres |
| `PG_PASSWORD` | Database password | (required) |
| `PG_DATABASE` | Database name | sql_monitor |
| **SQL Server** | | |
| `MSSQL_HOST` | SQL Server host | 127.0.0.1 |
| `MSSQL_PORT` | SQL Server port | 1433 |
| `MSSQL_USER` | SQL Server user | sa |
| `MSSQL_PASSWORD` | SQL Server password | (required) |
| `MSSQL_DATABASE` | Default monitoring database | master |
| **Scheduler** | | |
| `SCHEDULER_INTERVAL_SECONDS` | Collection interval (seconds) | 60 |
| **Email (SMTP)** | | |
| `SMTP_SERVER` | SMTP server address | smtp.example.com |
| `SMTP_PORT` | SMTP port | 587 |
| `SMTP_USER` | SMTP username | (optional) |
| `SMTP_PASSWORD` | SMTP password | (optional) |
| `ALERT_EMAILS` | Alert recipient email list | [] |
| **DingTalk** | | |
| `DINGTALK_WEBHOOK_URL` | DingTalk robot webhook URL | (optional) |
| **Logging** | | |
| `LOG_LEVEL` | Log level | INFO |
| **Auth / JWT** | | |
| `JWT_SECRET_KEY` | JWT secret | sql-monitor-secret-key-change-me-in-production |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_EXPIRE_HOURS` | JWT expiration (hours) | 24 |
| **Default Admin** | | |
| `DEFAULT_ADMIN_USERNAME` | Default admin username | Admin |
| `DEFAULT_ADMIN_PASSWORD` | Default admin password | Chuz0001 |

### 4.2 Runtime Configuration (Stored in Database)

The system also supports runtime configuration stored in the `system_configs` table, including:
- SQL Server connection configuration
- Collection and alert configuration
- Webhook notification configuration
- Multi-instance mode configuration
- Frontend access URL (frontend_url)
- Brand title (brand_title)

## 5. Deployment Guide

### 5.1 Requirements
- **Docker** >= 20.10 (Docker Desktop 4.x+ recommended)
- **Docker Compose** >= 2.0
- **Python** >= 3.12 (local development mode)
- **Node.js** >= 20 (local development mode)

### 5.2 Docker Deployment

#### 5.2.1 Prepare Environment Variables
```bash
# Create env file from template
cp .env.example .env

# Edit the .env file with actual database connection info
```

#### 5.2.2 Start Services
```bash
# Build and start all services (background)
docker-compose up -d

# Check service status
docker-compose ps

# View real-time logs
docker-compose logs -f
```

#### 5.2.3 Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove data volumes (wipes PostgreSQL data)
docker-compose down -v
```

### 5.3 Local Development

#### 5.3.1 Backend Development
```bash
# Enter backend directory
cd backend

# Create and configure env file
cp .env.example .env
# Edit .env, change PG_HOST to 127.0.0.1

# Install dependencies
pip install -r requirements.txt

# Start dev server (hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5.3.2 Frontend Development
```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start dev server (hot reload)
npm run dev
```

### 5.4 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:3000 | Monitoring platform web UI |
| **API Docs** | http://localhost:8000/docs | Swagger UI interactive docs |
| **API Docs (Alt)** | http://localhost:8000/redoc | ReDoc docs |
| **API Base URL** | http://localhost:8000 | RESTful API endpoints |
| **PostgreSQL** | localhost:5432 | Direct DB access (host only) |

## 6. Usage Guide

### 6.1 First Login
1. Visit http://localhost:3000
2. Log in with the default admin account:
   - Username: Admin
   - Password: Chuz0001
3. Change the default password immediately after first login

### 6.2 Configure Monitored Instances
1. Go to the "Instances" page
2. Click "Add Instance"
3. Fill in SQL Server connection info
4. Click "Test Connection" to verify
5. Save the configuration

### 6.3 Configure Alert Rules
1. Go to the "Alert Rules" page
2. Click "Add Rule"
3. Configure alert conditions:
   - Select metric category
   - Set comparison operator
   - Set threshold
   - Select severity
4. Optional: set a silent period
5. Save the rule

### 6.4 View Monitoring Data
1. **Dashboard**: View real-time key metrics
2. **Performance Trends**: View historical trend charts
3. **Deadlock Monitoring**: View deadlock event details
4. **Slow Query Analysis**: View slow query statistics

### 6.5 Generate Reports
1. Go to the "Reports" page
2. Select the report time range
3. Click "Generate Report"
4. View AI analysis recommendations
5. Optional: export as PDF

## 7. API Reference

### 7.1 Authentication
- `POST /api/auth/login`: User login, get JWT token
- `GET /api/auth/me`: Get current user info
- `POST /api/auth/change_password`: Change password
- `POST /api/auth/forgot_password`: Request password reset code (sent to email)
- `POST /api/auth/reset_password`: Reset password with verification code
- `PUT /api/auth/me`: Update current user profile (name, email)

### 7.2 User Management
- `GET /api/users`: Get user list
- `POST /api/users`: Create user
- `PUT /api/users/{id}`: Update user
- `DELETE /api/users/{id}`: Delete user

### 7.3 Monitoring Data
- `GET /api/metrics/realtime`: Get real-time metrics
- `GET /api/metrics/history`: Get historical metrics
- `GET /api/metrics/summary`: Get metric summary

### 7.4 Deadlocks
- `GET /api/deadlocks`: Get deadlock list
- `GET /api/deadlocks/{id}`: Get deadlock details
- `POST /api/deadlocks/{id}/analyze`: AI analysis of deadlock

### 7.5 Alerts
- `GET /api/alerts`: Get alert list
- `PUT /api/alerts/{id}/acknowledge`: Acknowledge alert

### 7.6 Alert Rules
- `GET /api/alert-rules`: Get alert rule list
- `POST /api/alert-rules`: Create alert rule
- `PUT /api/alert-rules/{id}`: Update alert rule
- `DELETE /api/alert-rules/{id}`: Delete alert rule
- `PUT /api/alert-rules/{id}/toggle`: Enable/disable alert rule

### 7.7 Instances
- `GET /api/instances`: Get instance list
- `POST /api/instances`: Create instance
- `PUT /api/instances/{id}`: Update instance
- `DELETE /api/instances/{id}`: Delete instance
- `POST /api/instances/{id}/test`: Test instance connection

### 7.8 Slow Queries
- `GET /api/slow-queries`: Get slow query list
- `GET /api/slow-queries/stats`: Get slow query statistics

### 7.9 Blocking
- `GET /api/blocking/realtime`: Get real-time blocking
- `GET /api/blocking/history`: Get blocking history

### 7.10 Disk
- `GET /api/disk/space`: Get disk space
- `GET /api/disk/history`: Get disk history

### 7.11 Indexes
- `GET /api/indexes/missing`: Get missing indexes
- `GET /api/indexes/fragmentation`: Get index fragmentation

### 7.12 Audit Logs
- `GET /api/audit-logs`: Get audit logs

### 7.13 Data Export
- `GET /api/export/metrics`: Export metrics data
- `GET /api/export/alerts`: Export alert data
- `GET /api/export/deadlocks`: Export deadlock data
- `GET /api/export/slow-queries`: Export slow query data

### 7.14 Notifications
- `GET /api/notifications`: Get notification list
- `PUT /api/notifications/{id}/read`: Mark notification as read
- `DELETE /api/notifications/{id}`: Delete notification
- `POST /api/notifications/read-all`: Mark all notifications as read

### 7.15 Reports
- `GET /api/reports/summary`: Get report summary
- `POST /api/reports/save`: Save report
- `GET /api/reports/history`: Get report history
- `DELETE /api/reports/history/{id}`: Delete report

### 7.16 Config
- `GET /api/config`: Get all config
- `GET /api/config/{key}`: Get single config
- `PUT /api/config/{key}`: Update config
- `POST /api/config/test_mssql`: Test SQL Server connection

### 7.17 Online Upgrade
- `GET /api/upgrade/check`: Check for new GitHub version
- `GET /api/upgrade/git-status`: View Git repository status
- `POST /api/upgrade/apply`: Execute online upgrade (git pull + Docker build)

## 8. Database Design

### 8.1 Core Tables

#### 8.1.1 metrics (Performance Metrics)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| category | String(50) | Metric category: cpu / memory / connection / io |
| metric_name | String(100) | Metric name |
| metric_value | Float | Metric value |
| unit | String(30) | Unit |
| collected_at | DateTime | Collection time |
| server_address | String(255) | Monitored SQL Server address |
| created_at | DateTime | Record creation time |

#### 8.1.2 deadlocks (Deadlock Events)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| occur_at | DateTime | Deadlock occurrence time |
| deadlock_xml | Text | Deadlock graph XML |
| victim_session_id | Integer | Victim session ID |
| server_address | String(255) | Monitored SQL Server address |
| analysis_result | Text | DeepSeek AI analysis result |
| created_at | DateTime | Record creation time |

#### 8.1.3 deadlock_sqls (Deadlock SQL Details)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| event_id | Integer | Related deadlock event ID |
| session_id | Integer | Session ID involved in deadlock |
| sql_text | Text | SQL statement executed by the session |
| isolation_level | String(50) | Transaction isolation level |
| involved_objects | String(500) | Involved objects |
| created_at | DateTime | Record creation time |

#### 8.1.4 alert_logs (Alert Logs)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| alert_type | String(50) | Alert type |
| severity | String(20) | Severity: low / medium / high / critical |
| message | Text | Alert message body |
| triggered_at | DateTime | Alert trigger time |
| acknowledged | Boolean | Whether acknowledged |
| acknowledged_at | DateTime | Acknowledgment time |
| notification_sent | Boolean | Whether notification was sent |
| created_at | DateTime | Record creation time |

#### 8.1.5 alert_rules (Alert Rules)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String(100) | Rule name |
| description | Text | Rule description |
| metric_category | String(50) | Metric category |
| metric_name | String(100) | Metric name |
| operator | String(10) | Comparison operator |
| threshold | Float | Alert threshold |
| severity | String(20) | Severity |
| enabled | Boolean | Whether enabled |
| silence_start | Time | Silent period start |
| silence_end | Time | Silent period end |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Update time |

#### 8.1.6 users (Users)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| username | String(50) | Login username |
| password_hash | String(255) | Password hash |
| role | String(20) | Role |
| full_name | String(100) | Full name |
| email | String(200) | Email address |
| is_active | Boolean | Whether active |
| last_login_at | DateTime | Last login time |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Update time |

#### 8.1.7 monitored_instances (Monitored Instances)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String(100) | Instance name |
| host | String(255) | SQL Server host address |
| port | Integer | SQL Server port |
| username | String(100) | Login username |
| password | String(200) | Login password |
| database_name | String(100) | Default database |
| is_active | Boolean | Whether collection is enabled |
| is_connected | Boolean | Current connection status: True=online, False=offline |
| last_connected_at | DateTime | Last successful connection time |
| last_disconnected_at | DateTime | Last disconnection time |
| connection_error | String(500) | Most recent connection error |
| description | Text | Instance description/notes |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Update time |

#### 8.1.8 slow_queries (Slow Queries)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| sql_hash | String(100) | SQL hash value |
| sql_text | Text | SQL statement |
| execution_count | Integer | Execution count |
| total_cpu_ms | Float | Total CPU time (ms) |
| total_logical_reads | Integer | Total logical reads |
| total_elapsed_ms | Float | Total elapsed time (ms) |
| avg_elapsed_ms | Float | Average elapsed time (ms) |
| last_execution_time | DateTime | Last execution time |
| collected_at | DateTime | Collection time |
| server_address | String(255) | Monitored SQL Server address |

#### 8.1.9 blocking_events (Blocking Events)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| blocking_session_id | Integer | Blocking session ID |
| blocked_session_id | Integer | Blocked session ID |
| blocking_sql_text | Text | SQL of the blocking session |
| blocked_sql_text | Text | SQL of the blocked session |
| wait_time_seconds | Float | Wait time (seconds) |
| wait_type | String(100) | Wait type |
| server_address | String(255) | Monitored SQL Server address |
| collected_at | DateTime | Collection time |
| created_at | DateTime | Record creation time |

#### 8.1.10 disk_space_records (Disk Space Records)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| database_name | String(100) | Database name |
| file_type | String(50) | File type: ROWS / LOG |
| file_name | String(255) | File name |
| physical_name | String(500) | Physical path |
| size_mb | Float | File size (MB) |
| used_mb | Float | Used space (MB) |
| free_mb | Float | Free space (MB) |
| usage_pct | Float | Usage percentage (%) |
| server_address | String(255) | Monitored SQL Server address |
| collected_at | DateTime | Collection time |
| created_at | DateTime | Record creation time |

#### 8.1.11 missing_indexes (Missing Indexes)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| database_name | String(100) | Database name |
| table_name | String(255) | Table name |
| equality_columns | String(500) | Equality columns |
| inequality_columns | String(500) | Inequality columns |
| included_columns | String(500) | Included columns |
| avg_total_user_cost | Float | Average total user cost |
| avg_user_impact | Float | Average user impact |
| user_seeks | Integer | User seek count |
| user_scans | Integer | User scan count |
| server_address | String(255) | Monitored SQL Server address |
| collected_at | DateTime | Collection time |
| created_at | DateTime | Record creation time |

#### 8.1.12 index_fragmentation (Index Fragmentation)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| database_name | String(100) | Database name |
| table_name | String(255) | Table name |
| index_name | String(255) | Index name |
| index_type | String(100) | Index type |
| avg_fragmentation_pct | Float | Average fragmentation (%) |
| page_count | Integer | Page count |
| server_address | String(255) | Monitored SQL Server address |
| collected_at | DateTime | Collection time |
| created_at | DateTime | Record creation time |

#### 8.1.13 audit_logs (Audit Logs)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Operating user ID |
| username | String(50) | Operating username |
| action | String(100) | Operation type |
| detail | Text | Operation details |
| ip_address | String(50) | IP address |
| created_at | DateTime | Operation time |

#### 8.1.14 system_configs (System Config)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| config_key | String(100) | Config key |
| config_value | Text | Config value |
| description | String(500) | Config description |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Update time |

#### 8.1.15 report_records (Report Records)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| title | String(200) | Report title |
| content | Text | Report content |
| report_data | Text | Report data (JSON) |
| ai_analysis | Text | AI analysis result |
| created_at | DateTime | Creation time |

## 9. Notes

### 9.1 Security
1. **Password security**: Always change default passwords in `.env`, especially `PG_PASSWORD` and `MSSQL_PASSWORD`
2. **JWT secret**: Change `JWT_SECRET_KEY` to a strong random string in production
3. **HTTPS**: HTTPS is recommended in production
4. **Firewall**: Restrict access to database ports

### 9.2 Performance
1. **Collection interval**: Adjust `SCHEDULER_INTERVAL_SECONDS` based on actual needs
2. **Data cleanup**: Regularly clean historical data to avoid oversized databases
3. **Index optimization**: Ensure PostgreSQL tables have appropriate indexes

### 9.3 Backup
1. **Database backup**: Regularly back up PostgreSQL data
2. **Config backup**: Back up `.env` and database config
3. **Log backup**: Regularly back up application logs

### 9.4 Monitoring
1. **Health checks**: Regularly check service health status
2. **Log monitoring**: Monitor application logs to catch anomalies early
3. **Resource monitoring**: Monitor server resource usage
