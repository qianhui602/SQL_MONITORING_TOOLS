# SQL Monitoring Platform - User Manual

[简体中文](../USER_MANUAL.md) | **English**

## 1. System Overview

The SQL Monitoring Platform is a web application for monitoring MS SQL Server performance, providing real-time monitoring, alert notifications, and historical analysis.

### 1.1 System Requirements
- Modern browser (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+)
- Screen resolution: 1280x720 or higher

### 1.2 Access
- Browser access: `http://<server-address>:3000`
- Default account: `Admin` / `Chuz0001`

> Please change the default password immediately after first login.

---

## 2. Login & Authentication

### 2.1 Logging In
1. Open your browser and visit the system address
2. Enter your username and password
3. Click the "Login" button

### 2.2 Password Recovery
1. Click "Forgot Password?" on the login page
2. Enter the email address used at registration
3. Check your email for the 6-digit verification code
4. Enter the code and a new password
5. Click "Reset Password"

### 2.3 Changing Password
1. Click the user avatar in the top-right corner
2. Select "Personal Settings"
3. Enter your current password and new password in the "Change Password" section
4. Click "Save Changes"

---

## 3. Dashboard (Overview)

The dashboard is the system home page, providing an overview of key performance metrics.

### 3.1 Statistic Cards
The top of the dashboard shows 9 statistic cards:
- **Database Instances**: online/offline instance count
- **CPU Usage**: current SQL Server CPU usage
- **Memory Usage**: memory used by SQL Server
- **Cache Hit Ratio**: buffer pool cache hit ratio
- **Active Connections**: current active database connections
- **Disk Usage**: disk space usage percentage
- **Batch Requests/sec**: batch requests per second
- **Lock Waits**: current lock wait count
- **Deadlock Events**: cumulative deadlock event count

#### Customizing Statistic Cards
1. Click the "Customize" button in the toolbar
2. In the "Statistic Cards" section, check/uncheck the cards to display
3. Settings are saved automatically and persist after refresh

#### Drag-and-Drop Reordering
- Hover over a card and drag the handle in the top-right corner to reorder cards

### 3.2 Database Connection Status
Shows real-time connection status of all monitored instances:
- **Online** (green): instance connected normally
- **Offline** (red): instance connection lost
- **Disabled** (gray): instance disabled

### 3.3 Performance Trend Charts
The chart area shows 6 trend charts:
- CPU usage trend
- Memory usage trend
- Connection count trend
- I/O latency trend
- Lock wait trend
- Batch request trend

#### Chart Operations
- **Select time range**: Last 1 hour / 6 hours / 24 hours / 7 days
- **Select instance**: dropdown to choose the instance to view
- **Refresh interval**: set auto-refresh interval (5/10/30/60 seconds or off)
- **Comparison mode**: compare with yesterday/last week/last month when enabled
- **View details**: click a chart to enlarge

#### Customizing Charts
1. Click the "Customize" button in the toolbar
2. In the "Charts" section, check/uncheck the charts to display
3. Click the "Sort" button to reorder charts

---

## 4. Performance Trends

Provides detailed historical trend analysis of performance metrics.

### 4.1 How to Use
1. Click "Performance Trends" in the left menu
2. Select a metric category (CPU, memory, connection, I/O)
3. Select a time range
4. View the trend charts

---

## 5. Deadlock Monitoring

Automatically captures and analyzes SQL Server deadlock events.

### 5.1 Viewing the Deadlock List
1. Click "Deadlock Monitoring" in the left menu
2. View the deadlock event list, including time, victim session, etc.

### 5.2 Viewing Deadlock Details
1. Click a deadlock record in the list
2. View the deadlock XML, involved SQL statements, and involved objects

### 5.3 AI Analysis
1. Click the "AI Analysis" button on the deadlock detail page
2. The system uses DeepSeek AI to analyze the deadlock cause
3. View optimization recommendations

---

## 6. Alert Management

### 6.1 Viewing Alerts
1. Click "Alert Management" in the left menu
2. View the alert list, including type, severity, trigger time
3. Filter by severity and time range

### 6.2 Acknowledging Alerts
1. Click the "Acknowledge" button in the alert list
2. The alert status changes to acknowledged

### 6.3 Notifications
- The system supports sound alerts; a tone plays when a new alert triggers
- Click the bell icon in the top bar to view notifications
- Click the "Mute" icon to toggle sound on/off

---

## 7. Alert Rules

### 7.1 Viewing Rules
1. Click "Alert Rules" in the left menu
2. View the list of all alert rules

### 7.2 Creating Rules
1. Click the "Add Rule" button
2. Fill in rule information:
   - Rule name
   - Metric category and metric name
   - Comparison operator (greater than, less than, equal, etc.)
   - Threshold
   - Severity (low, medium, high, critical)
3. Optional: set a silent period
4. Click "Save"

### 7.3 Enabling/Disabling Rules
- Toggle the switch next to a rule in the list to enable or disable it

---

## 8. Instance Management

Manages SQL Server monitoring instances.

### 8.1 Viewing Instances
1. Click "Instance Management" in the left menu
2. View the list of all monitored instances
3. View each instance's connection status (online/offline)

### 8.2 Adding Instances
1. Click the "Add Instance" button
2. Fill in connection information:
   - Instance name
   - Host address
   - Port (default 1433)
   - Username
   - Password
   - Default database
3. Click "Test Connection" to verify
4. Click "Save"

### 8.3 Editing Instances
1. Click the "Edit" button in the instance list
2. Modify configuration information
3. Click "Save"

### 8.4 Disabling/Enabling Instances
- Toggle the switch next to an instance in the list to disable or enable it

---

## 9. Slow Query Analysis

### 9.1 Viewing Slow Queries
1. Click "Slow Query Analysis" in the left menu
2. View the slow query list, including SQL text, execution count, CPU time, etc.

### 9.2 Viewing Statistics
1. Click the "Statistics" tab to view slow query summary statistics

---

## 10. Blocking Processes

### 10.1 Viewing Real-time Blocking
1. Click "Blocking Processes" in the left menu
2. View currently blocked processes

### 10.2 Viewing Historical Records
1. Switch to the "History" tab
2. View historical blocking events

---

## 11. Disk Space

### 11.1 Viewing Disk Space
1. Click "Disk Space" in the left menu
2. View disk usage of database files

### 11.2 Viewing Historical Trends
1. Switch to the "Historical Trends" tab
2. View historical disk space changes

---

## 12. Index Analysis

### 12.1 Viewing Missing Indexes
1. Click "Index Analysis" in the left menu
2. View missing indexes suggested by SQL Server

### 12.2 Viewing Index Fragmentation
1. Switch to the "Index Fragmentation" tab
2. View index fragmentation levels

---

## 13. System Reports

### 13.1 Generating Reports
1. Click "System Reports" in the left menu
2. Select the report time range
3. Click "Generate Report"
4. View report content and AI analysis recommendations

### 13.2 Viewing Historical Reports
1. Click a report in the report history list to view it

### 13.3 Exporting Reports
1. Click "Export PDF" on the report detail page

---

## 14. User Management (Admin)

### 14.1 Viewing Users
1. Click "User Management" in the left menu
2. View the list of all users

### 14.2 Creating Users
1. Click the "Add User" button
2. Fill in user information:
   - Username
   - Password
   - Full name
   - Email
   - Role (Super Admin/Admin/Read-only User)
3. Click "Save"

### 14.3 Editing Users
1. Click the "Edit" button in the user list
2. Modify user information
3. Click "Save"

### 14.4 Deleting Users
1. Click the "Delete" button in the user list
2. Confirm deletion

> Note: The super admin cannot be deleted.

---

## 15. Personal Settings

### 15.1 Changing Personal Information
1. Click the user avatar in the top-right corner
2. Select "Personal Settings"
3. Modify your name or email
4. Click "Save Changes"

### 15.2 Changing Password
1. On the Personal Settings page
2. Enter your current password and new password
3. Click "Save Changes"

---

## 16. System Settings (Admin)

### 16.1 Database Configuration
- Configure PostgreSQL database connection info

### 16.2 Collection Configuration
- Set the collection interval (default 60 seconds)

### 16.3 Alert Configuration
- Configure alert thresholds

### 16.4 Notification Configuration
- Configure email notifications (SMTP)
- Configure DingTalk robot
- Configure WeCom robot

### 16.5 Brand Customization
- Customize the system title
- Upload a custom logo

---

## 17. Online Upgrade (Admin)

### 17.1 Checking for Updates
1. Click "Online Upgrade" in the left menu
2. Click "Check for Updates"

### 17.2 Performing the Upgrade
1. Confirm the upgrade
2. The system automatically pulls the latest code and builds

---

## 18. Shortcuts

| Shortcut | Function |
|----------|----------|
| Click a chart | Enlarge to view chart details |
| Click a statistic card | Navigate to the corresponding feature page |
| Click instance status | Navigate to the instance management page |

---

## 19. FAQ

### Q: Cannot log in to the system?
A: Check:
1. Whether the username and password are correct
2. Whether the account is disabled
3. Whether the network connection is normal

### Q: Instance shows offline?
A: Check:
1. Whether the SQL Server service is running
2. Whether the network connection is normal
3. Whether the firewall allows port 1433
4. Whether the username and password are correct

### Q: Alerts are not triggering?
A: Check:
1. Whether the alert rule is enabled
2. Whether the threshold is reasonable
3. Whether you are in a silent period
4. Whether you are in a cooldown period

### Q: How do I change the collection interval?
A:
1. Log in as an administrator
2. Go to "System Settings"
3. Change the collection interval value
4. Save the settings

---

## 20. Contact Support

If you encounter any issues, please contact your system administrator or technical support.

**Sun Valley IT Department**
