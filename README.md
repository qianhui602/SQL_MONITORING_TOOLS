# SQL 监控平台

基于 FastAPI + Vue.js + PostgreSQL 的 MS SQL Server 性能监控与告警平台。

## 功能特性

- **性能监控**：CPU、内存、连接数、I/O、锁等待、批处理请求等 28 项指标
- **死锁检测**：自动捕获死锁事件，支持 DeepSeek AI 分析
- **慢查询分析**：TOP 20 慢查询识别与统计
- **阻塞链追踪**：实时监控 SQL Server 阻塞进程
- **磁盘空间监控**：数据库文件空间使用情况
- **索引分析**：缺失索引建议与碎片分析
- **多实例支持**：同时监控多个 SQL Server 实例
- **告警系统**：自定义告警规则，支持企业微信通知
- **在线升级**：支持通过管理后台一键升级
- **密码找回**：通过邮箱验证码重置密码
- **个人设置**：用户可修改姓名、邮箱等个人信息
- **安装引导**：首次部署提供可视化引导流程
- **声音提醒**：新告警声音通知，支持静音开关
- **品牌定制**：支持自定义系统标题和 Logo

## 快速开始

### 环境要求

- **Docker** >= 20.10（推荐 Docker Desktop 4.x+）
- **Docker Compose** >= 2.0（Docker Desktop 已内置）
- **Python** >= 3.12（本地开发模式）
- **Node.js** >= 20（本地开发模式）

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd SQL监控平台

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库连接信息

# 3. 启动服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 本地开发

**后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | 监控平台 Web UI |
| API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 后端 API | http://localhost:8000 | RESTful API 端点 |

## 项目结构

```
.
├── backend/              # FastAPI 后端服务
│   ├── app/              # 应用代码
│   │   ├── collectors/   # 指标采集器
│   │   ├── models/       # 数据模型
│   │   ├── routers/      # API 路由
│   │   └── services/     # 业务服务
│   ├── Dockerfile        # 后端 Docker 构建文件
│   └── requirements.txt  # Python 依赖
├── frontend/             # Vue.js 前端
│   ├── src/              # 前端源码
│   │   ├── views/        # 页面组件
│   │   │   ├── ForgotPassword.vue  # 找回密码
│   │   │   ├── ResetPassword.vue   # 重置密码
│   │   │   ├── Profile.vue         # 个人设置
│   │   │   └── Setup.vue           # 安装引导
│   │   ├── components/   # 公共组件
│   │   └── api/          # API 接口
│   ├── Dockerfile        # 前端 Docker 构建文件
│   └── package.json      # Node.js 依赖
├── Docs/                 # 项目文档
│   ├── PROJECT_DOCUMENTATION.md    # 项目文档
│   ├── TECHNICAL_DOCUMENTATION.md  # 技术文档
│   └── 指标监控说明文档.md          # 指标监控说明
├── docker-compose.yml    # Docker Compose 编排文件
└── .env                  # 环境变量配置
```

## 文档

详细文档请参阅 [Docs](./Docs/) 目录：

- [项目文档](./Docs/PROJECT_DOCUMENTATION.md) - 项目概述、功能模块、使用说明
- [技术文档](./Docs/TECHNICAL_DOCUMENTATION.md) - 技术架构、API 设计、部署架构
- [指标监控说明](./Docs/指标监控说明文档.md) - 监控指标详解、采集机制、数据存储

## 默认账号

- 用户名：`Admin`
- 密码：`Chuz0001`

> 请在首次登录后修改默认密码。

## 功能说明

- **密码找回**：在登录页点击"忘记密码"，输入注册邮箱获取验证码，凭验证码设置新密码
- **个人设置**：点击右上角用户菜单 → "个人设置"，可修改姓名和邮箱
- **安装引导**：首次部署访问时自动进入安装向导，引导完成数据库初始化和管理员账号创建
- **声音提醒**：顶部栏铃铛图标可查看通知，支持开启/关闭声音提醒

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

## 许可证

MIT License
