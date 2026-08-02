# SQL Monitoring Platform — Metrics Monitoring Guide

[简体中文](../指标监控说明文档.md) | **English**

## 1. Monitoring Architecture Overview

```
APScheduler (Scheduler, default 60 seconds)
    │
    ▼
SchedulerManager._collect_and_store()
    │
    ├──→ MetricsCollector (Performance Coordinator)
    │       ├── PerformanceCollector  ──  7 categories / 28 metrics
    │       ├── SlowQueryCollector    ──  TOP 20 slow queries
    │       └── DeadlockDetector      ──  deadlock events
    │
    ▼
PostgreSQL Storage (10 monitoring tables)
    │
    ▼
FastAPI Router Layer (6 modules)
    │
    ▼
Vue.js Frontend Display
```

## 2. Collection Mechanism

### 2.1 Scheduling

- **Driver**: APScheduler (AsyncIOScheduler)
- **Default interval**: every 60 seconds
- **Configurable**: change the `Collection Interval (seconds)` parameter on the System Settings page
- **Operating modes**:
  - **Single-instance mode**: uses the default SQL Server connection config
  - **Multi-instance mode**: iterates the `monitored_instances` table and collects independently for each active instance

### 2.2 Collection Flow

```
_collect_and_store()
    │
    ├─ 1. Load runtime config from system_configs
    ├─ 2. Determine single-instance / multi-instance mode
    ├─ 3. Establish SQL Server connection (pymssql)
    ├─ 4. Run 7 categories of DMV queries to collect performance metrics
    ├─ 5. Collect slow queries (TOP 20)
    ├─ 6. Run deadlock detection (XML parsing)
    ├─ 7. Batch write to PostgreSQL
    └─ 8. Trigger alert engine check
```

### 2.3 Data Isolation

- In multi-instance mode, each instance uses an independent connection
- Data is distinguished by the `server_address` field (format: `InstanceName(host:port)`)

---

## 3. Performance Metrics Explained

All metrics are collected from SQL Server Dynamic Management Views (DMVs), covering **7 categories / 28 metrics**.

### 3.1 CPU Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `cpu_usage` | System CPU usage | % | `sys.dm_os_ring_buffers` |
| `sql_cpu` | SQL Server process CPU usage | % | `sys.dm_os_sys_info` |

**Collection SQL**: extracts `ProcessUtilization` from `RING_BUFFER_SCHEDULER_MONITOR`.

### 3.2 Memory Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `sql_server_memory_mb` | SQL Server allocated memory | MB | `sys.dm_os_performance_counters` — Total Server Memory (KB) |
| `buffer_cache_hit_ratio` | Buffer cache hit ratio | % | `sys.dm_os_performance_counters` — Buffer cache hit ratio |
| `target_memory_mb` | SQL Server target memory | MB | `sys.dm_os_performance_counters` — Target Server Memory (KB) |
| `page_life_expectancy` | Page life expectancy | seconds | `sys.dm_os_performance_counters` — Page life expectancy |

> **Note**: `buffer_cache_hit_ratio` reflects data cache efficiency and should normally be > 95%. A `page_life_expectancy` below 300 seconds indicates memory pressure.

### 3.3 Connection Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `total_connections` | Total connections | count | `sys.dm_exec_connections` |
| `active_sessions` | Active sessions | count | `sys.dm_exec_sessions` WHERE status = 'running' |
| `user_connections` | User connections (counter) | count | `sys.dm_os_performance_counters` — User Connections |
| `user_processes` | User processes | count | `sys.dm_exec_sessions` WHERE is_user_process = 1 |

### 3.4 I/O Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `avg_read_latency_ms` | Average read latency | ms | `sys.dm_io_virtual_file_stats` |
| `avg_write_latency_ms` | Average write latency | ms | `sys.dm_io_virtual_file_stats` |
| `total_reads` | Total reads | count | `sys.dm_io_virtual_file_stats` |
| `total_writes` | Total writes | count | `sys.dm_io_virtual_file_stats` |
| `read_mb` | Total data read | MB | `sys.dm_io_virtual_file_stats` |
| `write_mb` | Total data written | MB | `sys.dm_io_virtual_file_stats` |

> **Note**: These metrics are cumulative since SQL Server startup; comparing values over time reveals storage performance trends.

### 3.5 OS Memory Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `total_physical_memory_gb` | Total physical memory | GB | `sys.dm_os_sys_info` |
| `available_physical_memory_gb` | Available physical memory | GB | `sys.dm_os_sys_memory` |
| `memory_usage_pct` | Memory usage | % | Computed: (total - available) / total |

### 3.6 Lock Wait Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `waiting_locks` | Locks waiting | count | `sys.dm_tran_locks` WHERE request_status = 'WAIT' |
| `lock_waits` | Lock wait tasks | count | `sys.dm_os_waiting_tasks` WHERE wait_type LIKE 'LCK%' |
| `avg_lock_wait_ms` | Average lock wait time | ms | `sys.dm_os_waiting_tasks` AVG(wait_duration_ms) |

### 3.7 Batch Request Metrics

| Metric | Meaning | Unit | Source View |
|--------|---------|------|-------------|
| `batch_requests_sec` | Batch requests per second | count/s | `sys.dm_os_performance_counters` — Batch Requests/sec |
| `sql_compilations_sec` | SQL compilations per second | count/s | `sys.dm_os_performance_counters` — SQL Compilations/sec |
| `sql_recompilations_sec` | SQL re-compilations per second | count/s | `sys.dm_os_performance_counters` — SQL Re-Compilations/sec |

> **Note**: An excessively high `sql_recompilations_sec` ratio may indicate missing parameterization or plan cache issues.

---

## 4. Specialized Monitoring

### 4.1 Slow Query Monitoring

| Item | Description |
|------|-------------|
| **Collection method** | Collects TOP 20 queries by total elapsed time each cycle |
| **Core SQL** | `sys.dm_exec_query_stats` + `sys.dm_exec_sql_text` |
| **Key metrics** | `sql_text`, `execution_count`, `total_cpu_ms`, `total_elapsed_ms`, `avg_elapsed_ms`, `total_logical_reads` |
| **Deduplication** | MD5 hash of SQL text for frontend aggregation |
| **Retention** | New records written each cycle; all history retained |

### 4.2 Deadlock Monitoring

| Item | Description |
|------|-------------|
| **Collection method** | Parses deadlock reports from the system health extended events session |
| **Core SQL** | `sys.dm_xe_session_targets` WHERE name = 'system_health' |
| **XML parsing** | Extracts victim_session_id, participating processes, SQL statements, isolation level, involved objects |
| **AI analysis** | One-click DeepSeek API call to analyze deadlock causes and provide optimization recommendations |
| **Storage** | Main table `deadlocks` + detail table `deadlock_sqls` (one-to-many) |

### 4.3 Blocking Chain Monitoring

| Item | Description |
|------|-------------|
| **Collection method** | Real-time query of current blocking chains |
| **Core SQL** | `sys.dm_exec_requests` WHERE blocking_session_id > 0 |
| **Key info** | block_spid (blocked session), blocking_spid (blocking source), wait_type, wait_time_ms, blocked_sql, blocking_sql |
| **Display** | Frontend sorts by `wait_time_ms` descending to highlight severe blocking |

### 4.4 Disk Space Monitoring

| Item | Description |
|------|-------------|
| **Collection method** | Queries master_files aggregated by database |
| **Core SQL** | `sys.master_files` grouped by database_id (excluding system databases) |
| **Key metrics** | `data_file_mb`, `log_file_mb`, `total_mb`, `used_mb`, `free_mb`, `usage_pct` |
| **Calculation** | free_mb = total_mb - used_mb; usage_pct = used_mb / total_mb * 100 |

### 4.5 Index Analysis

#### Missing Indexes

| Item | Description |
|------|-------------|
| **Collection method** | Queries missing indexes auto-suggested by SQL Server |
| **Core SQL** | `sys.dm_db_missing_index_details` + `sys.dm_db_missing_index_group_stats` |
| **Key metrics** | `avg_user_impact` (expected improvement %), `user_seeks/scans` |
| **Sorting** | Descending by `avg_user_impact` |

#### Index Fragmentation

| Item | Description |
|------|-------------|
| **Collection method** | Calls `sys.dm_db_index_physical_stats` |
| **Filters** | avg_fragmentation_pct > 5% AND page_count > 100 |
| **Index types** | Distinguishes CLUSTERED / NONCLUSTERED |

---

## 5. Data Storage

### 5.1 Monitoring Tables

| Table | Purpose | Volume | Retention Policy |
|-------|---------|--------|------------------|
| `metrics` | General performance metrics (7 categories, 28 items) | Large | Recommend periodic cleanup |
| `slow_queries` | Slow query records | Large | Recommend periodic cleanup |
| `deadlocks` | Deadlock events | Medium | Recommend retention |
| `deadlock_sqls` | Deadlock-related SQL details | Medium | Cascades with parent table |
| `blocking_events` | Blocking event history | Large | Recommend periodic cleanup |
| `disk_space_records` | Disk space history | Medium | Recommend periodic cleanup |
| `missing_indexes` | Missing index suggestions | Medium | Recommend periodic cleanup |
| `index_fragmentation` | Index fragmentation records | Medium | Recommend periodic cleanup |

### 5.2 `metrics` Table Structure

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER (PK) | Primary key |
| category | VARCHAR(50) | Category: cpu / memory / connection / io / os_memory / locks / batch_requests |
| metric_name | VARCHAR(100) | Metric name, e.g. cpu_usage |
| metric_value | DOUBLE | Metric value |
| unit | VARCHAR(20) | Unit: %, MB, GB, ms, count |
| collected_at | TIMESTAMPTZ | Collection time |
| server_address | VARCHAR(255) | Instance identifier |

---

## 6. Alert Rules

### 6.1 Built-in Alerts

| Alert | Trigger Condition | Severity | Cooldown |
|-------|-------------------|----------|----------|
| High memory | OS memory usage > 85% sustained for ≥ 5 minutes | critical | 10 minutes |
| Deadlock detected | New record appears in deadlock events table | high | 5 minutes |
| Collection interrupted | No new data for 3 consecutive collection cycles | high | 15 minutes |

### 6.2 Custom Alerts

Custom alerts can be created on the Alert Rules page, supporting:
- **Metric selection**: match any collected metric by category + name
- **Condition operators**: `>` / `<` / `>=` / `<=` / `=`
- **Silent periods**: configure time windows where alerts do not fire
- **Multi-channel notifications**: in-app notifications + WeCom group robot

---

## 7. Complete Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  SQL Server (Monitored Target)                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ sys.dm_os_* (system info / system memory)          │   │
│  │ sys.dm_os_performance_counters (perf counters)     │   │
│  │ sys.dm_os_ring_buffers (scheduler/CPU)             │   │
│  │ sys.dm_exec_* (connections/sessions/requests/query) │  │
│  │ sys.dm_io_virtual_file_stats (I/O stats)           │   │
│  │ sys.dm_tran_locks (lock info)                      │   │
│  │ sys.dm_db_missing_index_details (missing indexes)  │   │
│  │ sys.dm_db_index_physical_stats (index fragmentation)│  │
│  │ sys.master_files (disk space)                      │   │
│  │ sys.dm_xe_session_targets (extended events/deadlock)│  │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │ pymssql connection
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Python Collection Layer                                 │
│  MetricsCollector.collect_all_metrics()                   │
│    ├── PerformanceCollector.collect_all()  ──── 28 metrics │
│    ├── SlowQueryCollector.collect_top20()  ── slow queries│
│    └── DeadlockDetector.check_deadlocks()  ── deadlocks   │
└──────────────────────┬──────────────────────────────────┘
                       │ asyncpg write
                       ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL (Data Storage)                                │
│  8 monitoring tables + 2 alert/config tables              │
└──────────────────────┬──────────────────────────────────┘
                       │ FastAPI query
                       ▼
┌─────────────────────────────────────────────────────────┐
│  API Layer (FastAPI + router modules)                     │
│  6 monitoring routers + alert/config/audit routers        │
└──────────────────────┬──────────────────────────────────┘
                       │ Axios JSON
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend Display (Vue 3 + ECharts + Element Plus)       │
│  Dashboard / Trends / Deadlocks / Slow Queries            │
│  Blocking / Disk / Indexes / Alerts / Reports             │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Performance & Security

### 8.1 Impact of Collection on Source Database

- All queries target **DMVs** and **system catalog views**; no user tables are locked
- Independent connection via `pymssql`, closed immediately after collection
- The default 60-second collection interval does not cause significant load on the source database

### 8.2 Connection Security

- SQL Server connection info is stored in PostgreSQL; passwords are stored unencrypted in the database
- Grant the monitoring account minimal permissions: `VIEW SERVER STATE` + `VIEW DATABASE STATE` is sufficient

### 8.3 Data Storage

- Monitoring data is stored in a dedicated PostgreSQL database
- For large tables such as `metrics` and `slow_queries`, partition by time and periodically clean up expired data
