# SQL Monitoring Platform

A performance monitoring and alerting platform for MS SQL Server, built with FastAPI + Vue.js + PostgreSQL.

**English** | [简体中文](./README.md)

## Features

### Core Monitoring
- **Performance Monitoring**: 28 metrics covering CPU, memory, connections, I/O, lock waits, batch requests, etc.
- **SQL Disconnection Monitoring**: Actively probes SQL Server connectivity; automatically alerts on disconnect/recovery
- **Deadlock Detection**: Automatically captures deadlock events, supports DeepSeek AI analysis
- **Slow Query Analysis**: Top 20 slow query identification and statistics
- **Blocking Chain Tracking**: Real-time monitoring of SQL Server blocking processes
- **Disk Space Monitoring**: Database file space usage
- **Index Analysis**: Missing index suggestions and fragmentation analysis
- **Multi-instance Support**: Monitor multiple SQL Server instances simultaneously

### Alerts & Notifications
- **Alert System**: Custom alert rules with multi-channel combined notifications
- **Feishu App Notification**: Critical errors are pushed directly to designated users via a Feishu custom app; recipients support both open_id and email address (receive_id_type auto-detected), with specific failure reasons surfaced on errors
- **Group Robot Webhooks**: DingTalk / WeCom / Feishu group robot webhook push
- **Email Notifications**: Alert emails via SMTP
- **Channel Modal Config & Test**: Each notification channel in System Settings is presented as a card; click to configure in a modal dialog and send a test message with one click
- **Sound Alerts**: Audible notification for new alerts, with mute toggle
- **Connection Status Alerts**: Automatic alerts on instance offline/recovery

### Users & Permissions
- **Role-based Access**: Super Admin, Admin, and Read-only User roles
- **Password Recovery**: Reset password via email verification code
- **Personal Settings**: Users can update their name, email, etc.

### System Features
- **Online Upgrade**: One-click upgrade via the admin console
- **Installation Wizard**: Visual guided setup for first-time deployment
- **Brand Customization**: Custom system title and logo
- **Dark Mode**: Dark/light theme switching

### UI Features
- **Modern Design**: Glassmorphism style, gradient decorations, micro-interaction animations
- **Responsive Layout**: Optimized for desktop and tablet devices
- **Real-time Refresh**: Configurable auto-refresh interval (5s/10s/30s/60s)
- **Customizable Dashboard**: Show/hide and reorder statistic cards and charts

## Quick Start

### Requirements

- **Docker** >= 20.10 (Docker Desktop 4.x+ recommended)
- **Docker Compose** >= 2.0 (bundled with Docker Desktop)
- **Python** >= 3.12 (local development mode)
- **Node.js** >= 20 (local development mode)

### Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd SQL监控平台

# 2. Configure environment variables
cp .env.example .env
# Edit the .env file and fill in database connection info

# 3. Start services
docker-compose up -d

# 4. Check service status
docker-compose ps
```

### Local Development

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend UI | http://localhost:3000 | Monitoring platform web UI |
| API Docs | http://localhost:8000/docs | Swagger UI interactive docs |
| Backend API | http://localhost:8000 | RESTful API endpoints |

## Project Structure

```
.
├── backend/              # FastAPI backend service
│   ├── app/              # Application code
│   │   ├── collectors/   # Metric collectors
│   │   ├── models/       # Data models
│   │   ├── routers/      # API routers
│   │   └── services/     # Business services
│   ├── Dockerfile        # Backend Docker build file
│   └── requirements.txt  # Python dependencies
├── frontend/             # Vue.js frontend
│   ├── src/              # Frontend source code
│   │   ├── views/        # Page components
│   │   │   ├── ForgotPassword.vue  # Forgot password
│   │   │   ├── ResetPassword.vue   # Reset password
│   │   │   ├── Profile.vue         # Personal settings
│   │   │   └── Setup.vue           # Installation wizard
│   │   ├── components/   # Shared components
│   │   └── api/          # API client
│   ├── Dockerfile        # Frontend Docker build file
│   └── package.json      # Node.js dependencies
├── Docs/                 # Project documentation
│   ├── PROJECT_DOCUMENTATION.md    # Project documentation
│   ├── TECHNICAL_DOCUMENTATION.md  # Technical documentation
│   ├── 指标监控说明文档.md          # Metrics monitoring guide
│   └── en/               # English documentation
├── docker-compose.yml    # Docker Compose orchestration
└── .env                  # Environment variables
```

## Documentation

For detailed documentation, see the [Docs](./Docs/) directory:

- [Project Documentation](./Docs/PROJECT_DOCUMENTATION.md) - Project overview, feature modules, usage guide
- [Technical Documentation](./Docs/TECHNICAL_DOCUMENTATION.md) - Technical architecture, API design, deployment architecture
- [User Manual](./Docs/USER_MANUAL.md) - System operation guide, feature usage
- [Metrics Monitoring Guide](./Docs/指标监控说明文档.md) - Metric details, collection mechanisms, data storage

**English versions:**

- [Project Documentation (EN)](./Docs/en/PROJECT_DOCUMENTATION.md)
- [Technical Documentation (EN)](./Docs/en/TECHNICAL_DOCUMENTATION.md)
- [User Manual (EN)](./Docs/en/USER_MANUAL.md)
- [Metrics Monitoring Guide (EN)](./Docs/en/METRICS_MONITORING.md)

## Default Account

- Username: `Admin`
- Password: `Chuz0001`

> Please change the default password after your first login.

## Feature Notes

- **Password Recovery**: Click "Forgot Password" on the login page, enter your registered email to receive a verification code, then set a new password
- **Personal Settings**: Click the user menu at the top right → "Personal Settings" to update your name and email
- **Installation Wizard**: On first deployment, the setup wizard guides you through database initialization and admin account creation
- **Sound Alerts**: Click the bell icon in the top bar to view notifications; toggle sound alerts on/off
- **Notification Channels**: Admins configure email, DingTalk, WeCom, and Feishu channels as cards under "System Settings → Notification Service"; click a card to open its config modal and send test messages. Feishu app notifications accept either an email address or open_id as the recipient

## Upgrade Guide

The system automatically checks for new versions. When an update is available, a yellow dot appears next to the version number at the bottom of the sidebar, and an upgrade banner pops up at the bottom of the page.

### Manual Upgrade Steps

#### Docker Deployment Upgrade (Recommended)

```bash
# 1. Enter the project directory
cd SQL_MONITORING_TOOLS

# 2. Pull the latest code
git pull origin master

# 3. Rebuild and restart containers (data is preserved automatically)
docker-compose up -d --build

# 4. Verify service status
docker-compose ps
```

#### Local Development Environment Upgrade

```bash
# 1. Enter the project directory
cd SQL_MONITORING_TOOLS

# 2. Pull the latest code
git pull origin master

# 3. Upgrade backend dependencies
cd backend
pip install -r requirements.txt

# 4. Upgrade frontend dependencies
cd ../frontend
npm install

# 5. Restart the backend service
cd ../backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Restart the frontend dev server (in another terminal)
cd frontend
npm run dev
```

### Upgrade Notes

| Item | Description |
|------|-------------|
| Database | Database migrations run automatically during upgrade, no manual action needed |
| Config files | Existing system config (branding, alert rules, etc.) is preserved |
| User data | All user accounts and audit logs are retained |
| Docker volumes | Data is stored in volumes with Docker deployments; rebuilding containers does not lose data |

### Upgrade Scripts

You can save the following scripts as `upgrade.sh` (Linux/Mac) or `upgrade.bat` (Windows) for quick upgrades:

**Linux/Mac (`upgrade.sh`)**

```bash
#!/bin/bash
echo "=== SQL Monitoring Platform Upgrade Script ==="
echo ""

# Pull the latest code
echo "[1/4] Pulling the latest code..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ Failed to pull code. Please check your network connection"
    exit 1
fi

# Detect deployment type
if [ -f "docker-compose.yml" ] && command -v docker &> /dev/null; then
    echo "[2/4] Docker deployment detected, rebuilding..."
    docker-compose up -d --build
    echo "[3/4] Cleaning up old images..."
    docker image prune -f
    echo "[4/4] Verifying service status..."
    docker-compose ps
else
    echo "[2/4] Local deployment detected, installing dependencies..."
    cd backend && pip install -r requirements.txt
    cd ../frontend && npm install
    echo "[3/4] Dependencies installed"
    echo "[4/4] Please restart the backend and frontend services manually"
fi

echo ""
echo "✅ Upgrade complete!"
```

**Windows (`upgrade.bat`)**

```bat
@echo off
echo === SQL Monitoring Platform Upgrade Script ===
echo.

echo [1/4] Pulling the latest code...
git pull origin master
if %errorlevel% neq 0 (
    echo ❌ Failed to pull code. Please check your network connection
    pause
    exit /b 1
)

echo [2/4] Detecting deployment type...
if exist "docker-compose.yml" (
    echo Docker deployment detected, rebuilding...
    docker-compose up -d --build
    echo [3/4] Cleaning up old images...
    docker image prune -f
    echo [4/4] Verifying service status...
    docker-compose ps
) else (
    echo Local deployment detected, installing dependencies...
    cd backend && pip install -r requirements.txt
    cd ../frontend && npm install
    echo [3/4] Dependencies installed
    echo [4/4] Please restart the backend and frontend services manually
)

echo.
echo ✅ Upgrade complete!
pause
```

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Check service status
docker-compose ps
```

## License

MIT License
