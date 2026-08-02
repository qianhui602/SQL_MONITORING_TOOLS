# 变更记录 - AI 助手重构：聊天式交互、上下文追问、HTML渲染

- **日期**: 2026-07-30 09:20
- **类型**: 新增功能 / Bug修复
- **影响范围**: AI 助手前端页面、后端任务执行引擎、Tab 标签管理

## 变更内容

### 1. 步骤结果展示（Issue #1）
已完成的诊断步骤可通过点击展开箭头（▼）查看详细分析结果。步骤卡片标题和描述始终可见，结果内容在展开后显示。

### 2. 聊天式追问交互（Issue #2 & #3）
任务执行完成后，底部输入框始终可见（不再被遮挡）。用户可在输入框中输入追问内容，AI 基于之前的分析上下文进行回答，形成多轮对话。追问结果以聊天气泡形式展示在步骤列表下方。

### 3. Markdown → HTML 渲染（Issue #4）
重写了 `renderMarkdown` 函数，支持以下 Markdown 格式的 HTML 渲染：
- 标题（h1-h4）
- 加粗、斜体
- 无序列表、有序列表
- 代码块（```...```）和行内代码
- 引用块（>）
- 分割线（---）
- 链接
- 自动换行

### 4. Tab 标签 Unknown 修复（Issue #5）
修改 `addTab` 函数，优先使用菜单项的已翻译标签（`menuItem.label`），如果菜单项不存在则回退到路由 `meta.title` 翻译，如果两者都为空则跳过添加 Tab。彻底消除 "Unknown" 标签。

### 5. 后端追问 API
新增 `POST /api/ai/tasks/{task_id}/followup` 端点，接收 `{ query: str }` 请求体：
- 加载任务历史步骤作为上下文
- 构建多轮对话消息列表（system + user + assistant 交替）
- 调用 AI 生成回答，保存为 `step_type="followup"` 的步骤记录
- 新增 `chat_completion()` 和 `get_base_url()` 公共函数

### 6. i18n 翻译
中英文新增以下翻译键：
- `followUpPlaceholder`：追问输入框占位符
- `followUpFailed`：追问失败提示
- `userMessage`：用户消息标签
- `aiResponse`：AI 回复标签
- `stepResult`：步骤结果标签
- `followUp`：追问标签

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|------|------|
| frontend/src/views/AiAssistant.vue | 修改 | 完整重写：聊天式布局、Markdown渲染、追问功能 |
| frontend/src/components/Layout.vue | 修改 | 修复 addTab 函数，消除 Unknown 标签 |
| frontend/src/api/index.js | 修改 | 新增 followUpAiTask API 函数 |
| frontend/src/i18n/zh-CN.js | 修改 | 新增 6 个中文翻译键 |
| frontend/src/i18n/en-US.js | 修改 | 新增 6 个英文翻译键 |
| backend/app/routers/ai_tasks.py | 修改 | 新增 followup 端点和请求模型 |
| backend/app/services/ai_executor.py | 修改 | 新增 execute_followup 函数 |
| backend/app/services/deepseek.py | 修改 | 新增 chat_completion 和 get_base_url 公共函数 |

## Git 信息
- commit (功能): `aae313e`
- commit (修复): `9441f9e` — 修复 create_task 缺少 return 导致任务创建失败
- 分支: `master`
- 推送: `02d01c5..9441f9e master -> master`
