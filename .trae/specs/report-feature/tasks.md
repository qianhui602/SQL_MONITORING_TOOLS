# 任务列表

## 任务 1：后端 - 报告数据模型（ReportRecord）
- [ ] 在 `backend/app/models/` 下新建 `report.py`，定义 `ReportRecord` 模型：
  - `id`: 主键
  - `title`: 报告标题
  - `start_time`: 报告时间范围开始
  - `end_time`: 报告时间范围结束
  - `summary_data`: JSON字段，存储报告的聚合摘要数据快照
  - `created_at`: 创建时间
  - `created_by`: 创建用户ID
- [ ] 在 `backend/app/models/__init__.py` 中导出 `ReportRecord`

## 任务 2：后端 - 报告聚合API（/api/reports/summary）
- [ ] 在 `backend/app/routers/` 下新建 `reports.py`
- [ ] 实现 `GET /api/reports/summary` 端点：
  - 参数：`start_time`、`end_time`
  - 聚合数据范围：
    - 调用 `getMetricsSummary()` 获取概览摘要
    - 调用 `getHistoryMetrics()` 获取各分类趋势数据（CPU/内存/连接数/IO）
    - 查询死锁事件（`DeadlockEvent`）统计次数和列表
    - 查询慢查询记录（`SlowQueryRecord`）统计数量和TOP N
    - 查询阻塞事件（`BlockingEvent`）统计
    - 查询磁盘空间（`DiskSpaceRecord`）最新记录
    - 查询索引分析（缺失索引数、碎片率高的索引数）
  - 返回统一的报告数据JSON
- [ ] 实现 `POST /api/reports/save` 端点：保存报告历史记录
- [ ] 实现 `GET /api/reports/history` 端点：获取历史报告列表
- [ ] 实现 `DELETE /api/reports/history/{id}` 端点：删除历史报告
- [ ] 在 `backend/app/routers/__init__.py` 中注册 `reports` 路由

## 任务 3：后端 - DeepSeek AI报告分析
- [ ] 在 `backend/app/services/deepseek.py` 中新增 `analyze_report` 函数
  - 接收报告聚合数据作为参数
  - 构建面向性能评估的Prompt
  - 调用DeepSeek API生成分析结论
  - 返回Markdown格式的分析结果
- [ ] 在报告聚合API中：当聚合数据完成后，异步调用DeepSeek分析，将结果一并返回

## 任务 4：前端 - 安装PDF导出依赖
- [ ] 在 `frontend/` 目录下执行 `npm install jspdf html2canvas`
- [ ] 确认依赖安装成功

## 任务 5：前端 - 新增报告页面路由
- [ ] 在 `frontend/src/router/index.js` 中新增 `/report` 路由，指向 `Report.vue`
- [ ] 在 `frontend/src/components/Layout.vue` 的侧边栏中添加"系统报告"导航项

## 任务 6：前端 - 实现报告页面（Report.vue）
- [ ] 创建 `frontend/src/views/Report.vue`，包含以下功能区域：
  - **顶部工具栏**：
    - 时间范围选择器（最近1小时/6小时/24小时/7天/自定义日期范围）
    - "生成报告"按钮（带加载状态）
    - "导出PDF"按钮
    - "历史记录"按钮
  - **概览摘要区域**：展示CPU/内存/连接数/缓存命中率/死锁数/慢查询数的卡片
  - **性能趋势区域**：内嵌CPU/内存/连接数/IO共4个ECharts图表
  - **死锁分析区域**：死锁次数统计 + 死锁事件表格
  - **慢查询分析区域**：慢查询数量、平均耗时、TOP慢查询列表
  - **阻塞/磁盘/索引状态区域**：简要展示阻塞事件数、磁盘使用率、索引状况
  - **AI分析与建议区域**：渲染DeepSeek返回的Markdown内容
  - **加载状态**：骨架屏或加载动画
  - **错误状态**：错误提示与重试
- [ ] 集成 `html2canvas` + `jspdf` 实现PDF导出功能
  - 导出时先将报告区域截图
  - 按A4纸张大小分页
  - 添加页码和标题
  - 自动触发下载

## 任务 7：前端 - 新增API函数
- [ ] 在 `frontend/src/api/index.js` 中新增：
  - `getReportSummary(params)` - 获取报告聚合数据
  - `saveReport(data)` - 保存报告历史
  - `getReportHistory()` - 获取历史报告列表
  - `deleteReportHistory(id)` - 删除历史报告

## 任务 8：前端 - 报告历史记录面板
- [ ] 在报告页面新增历史记录下拉面板或侧滑面板
- [ ] 展示历史记录列表（生成时间、时间范围）
- [ ] 支持点击加载历史报告
- [ ] 支持删除历史记录
- [ ] 支持重新下载历史报告的PDF

## 任务 9：数据库迁移
- [ ] 在 `backend/app/init_db.py` 中添加 `ReportRecord` 表的自动建表逻辑
- [ ] 确保新表在应用启动时自动创建

# 任务依赖关系
- [任务 1] 是 [任务 2] 的前置依赖
- [任务 2] 是 [任务 6] 的前置依赖
- [任务 3] 是 [任务 6] 的前置依赖
- [任务 4] 是 [任务 6] 的前置依赖
- [任务 5] 是 [任务 6] 的前置依赖
- [任务 9] 是 [任务 1] 的后置依赖
- [任务 7] 可与 [任务 6] 并行
- [任务 8] 是 [任务 6] 的子任务

# 可并行任务
- [任务 1] 和 [任务 4] 和 [任务 5] 可并行执行
- [任务 2] 和 [任务 3] 可并行执行（依赖 [任务 1]）
