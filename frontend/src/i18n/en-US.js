export default {
  common: {
    query: 'Query',
    search: 'Search',
    reset: 'Reset',
    confirm: 'Confirm',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    save: 'Save',
    loading: 'Loading...',
    empty: 'No data',
    retry: 'Retry',
    refresh: 'Refresh',
    export: 'Export',
    exporting: 'Exporting...',
    exportFailed: 'Export failed. Please try again.',
    total: 'Total',
    items: 'items',
    page: 'page',
    perPage: 'Per page',
    prevPage: 'Previous',
    nextPage: 'Next',
    pageInfo: 'Page {page} / {total}',
    all: 'All',
    enable: 'Enable',
    disable: 'Disable',
    enabled: 'Enabled',
    disabled: 'Disabled',
    submit: 'Submitting...',
    optional: 'optional',
    seconds: 'sec',
    minutes: 'min',
    hours: 'hours',
    day: 'days',
    online: 'Online',
    offline: 'Offline',
    disabledStatus: 'Disabled',
    connectError: 'Connection error',
    operationFailed: 'Operation failed',
    deleteFailed: 'Delete failed',
    confirmDelete: 'Are you sure you want to delete "{name}"?',
    serverAddress: 'Server Address',
    port: 'Port',
    account: 'Account',
    password: 'Password',
    database: 'Database',
    operation: 'Actions',
  },
  layout: {
    version: 'Version',
    notifications: 'Notifications',
    markAllRead: 'Mark all read',
    noNotifications: 'No notifications',
    soundReminder: 'Sound reminder',
    desktopNotification: 'Desktop notification',
    switchToDark: 'Switch to dark mode',
    switchToLight: 'Switch to light mode',
    personalSettings: 'Profile',
    logout: 'Sign out',
    closeOthers: 'Close others',
    closeCurrent: 'Close current',
    closeAll: 'Close all',
    newVersion: 'New version v{version} available',
    viewUpgradeGuide: 'View upgrade guide',
    later: 'Later',
    copyright: 'Sun Valley IT Dept 2026',
    menu: {
      dashboard: 'Dashboard',
      trends: 'Performance',
      deadlocks: 'Deadlocks',
      alerts: 'Alerts',
      slowQueries: 'Slow Queries',
      blocking: 'Blocking',
      disk: 'Disk Space',
      indexes: 'Indexes',
      report: 'Report',
      alertRules: 'Alert Rules',
      instances: 'Instances',
      auditLogs: 'Audit Logs',
      settings: 'Settings',
      users: 'Users',
      help: 'Help',
      aiAssistant: 'AI Assistant',
    },
    langSwitch: {
      'zh-CN': '中文',
      'en-US': 'English',
    },
  },
  dashboard: {
    statCards: {
      cpu: 'CPU Usage',
      memory: 'Memory Usage',
      connections: 'Active Connections',
      cache: 'Cache Hit Rate',
      disk: 'Disk Usage',
      batch: 'Batch/sec',
      locks: 'Lock Waits',
      deadlock: 'Deadlocks',
      instances: 'DB Instances',
    },
    noInstances: 'No instances',
    dbStatus: 'Database Connection Status',
    allInstances: 'All instances',
    instanceSelect: 'All instances',
    timeRange: 'Time Range',
    refresh: 'Refresh',
    compare: 'Compare',
    customize: 'Customize',
    sort: 'Sort',
    statCardsTitle: 'Stat Cards',
    chartsTitle: 'Charts',
    chartSort: 'Chart Order (click arrows to reorder)',
    resetChartOrder: 'Reset order',
    compareYesterday: 'Yesterday',
    compareLastWeek: 'Last week',
    compareLastMonth: 'Last month',
    charts: {
      cpu: 'CPU Usage Trend',
      memory: 'Memory Usage Trend',
      connections: 'Connections Trend',
      io: 'IO Latency Trend',
      locks: 'Lock Waits Trend',
      batch: 'Batch Requests Trend',
    },
    ranges: {
      '1h': 'Last 1 hour',
      '6h': 'Last 6 hours',
      '24h': 'Last 24 hours',
      '7d': 'Last 7 days',
    },
    refreshOptions: {
      '5s': '5 sec',
      '10s': '10 sec',
      '30s': '30 sec',
      '60s': '60 sec',
      off: 'Off',
    },
    details: 'Details',
    chartDetail: 'Chart Details',
    dragSort: 'Drag to sort',
    customLayoutSort: 'Custom layout order',
    moveUp: 'Move up',
    moveDown: 'Move down',
    series: {
      cpuUsage: 'CPU Usage',
      memoryUsage: 'Memory Usage',
      activeConnections: 'Active Connections',
      ioReadLatency: 'Read Latency',
      ioWriteLatency: 'Write Latency',
      lockWaits: 'Lock Waits',
      batchRequests: 'Batch Requests/sec',
    },
    previousPeriod: 'Previous Period',
  },
  trends: {
    instance: 'Instance',
    allInstances: 'All instances',
    metricCategory: 'Category',
    timeRange: 'Time Range',
    metricName: 'Metrics',
    categories: {
      cpu: 'CPU',
      memory: 'Memory',
      connections: 'Connections',
      io: 'IO',
      locks: 'Locks',
      batch_requests: 'Batch Requests',
    },
    metrics: {
      cpu_usage: 'CPU Usage',
      sql_cpu: 'SQL CPU',
      sql_server_memory_mb: 'Memory (MB)',
      buffer_cache_hit_ratio: 'Cache Hit Rate',
      target_memory_mb: 'Target Memory (MB)',
      page_life_expectancy: 'Page Life Expectancy',
      total_connections: 'Total Connections',
      active_sessions: 'Active Sessions',
      user_connections: 'User Connections',
      user_processes: 'User Processes',
      avg_read_latency_ms: 'Read Latency (ms)',
      avg_write_latency_ms: 'Write Latency (ms)',
      total_reads: 'Total Reads',
      total_writes: 'Total Writes',
      read_mb: 'Read MB',
      write_mb: 'Write MB',
      waiting_locks: 'Waiting Locks',
      lock_waits: 'Lock Waits',
      avg_lock_wait_ms: 'Avg Lock Wait (ms)',
      batch_requests_sec: 'Batch Requests/sec',
      sql_compilations_sec: 'SQL Compilations/sec',
      sql_recompilations_sec: 'SQL Recompilations/sec',
    },
  },
  deadlocks: {
    instance: 'Instance',
    allInstances: 'All instances',
    startTime: 'Start Time',
    endTime: 'End Time',
    user: 'User',
    host: 'Host (Device)',
    application: 'Application',
    userPlaceholder: 'Username, e.g. Sboadmin',
    hostPlaceholder: 'Hostname, e.g. MSSAP01C',
    appPlaceholder: 'App name, e.g. SAP Business One',
    occurTime: 'Occurrence Time',
    victimSessionId: 'Victim Session ID',
    serverAddress: 'SQL Server Address',
    relatedSql: 'Related SQL Statements',
    session: 'Session',
    userLabel: 'User:',
    hostLabel: 'Host:',
    appLabel: 'App:',
    isolationLabel: 'Isolation:',
    involvedObjects: 'Involved Objects',
    aiAnalysis: 'DeepSeek AI Analysis',
    aiButton: 'AI Analysis',
    analyzing: 'Analyzing...',
    aiHint: 'Click "AI Analysis" to analyze deadlock causes using DeepSeek',
    rawXml: 'Raw Deadlock XML',
    noData: 'None',
    error: 'Failed to load deadlocks. Please try again.',
    fetchFailed: 'Failed to load deadlocks',
  },
  alerts: {
    severity: 'Severity',
    startTime: 'Start Time',
    endTime: 'End Time',
    alertType: 'Alert Type',
    message: 'Message',
    triggerTime: 'Trigger Time',
  },
  slowQueries: {
    instance: 'Instance',
    allInstances: 'All instances',
    timeRange: 'Time Range',
    queryText: 'Query Text',
    execCount: 'Executions',
    totalCpuTime: 'Total CPU Time (ms)',
    totalLogicalReads: 'Total Logical Reads',
    avgDuration: 'Avg Duration (ms)',
    lastExecTime: 'Last Execution',
    collectedAt: 'Collected At',
    fullSql: 'Full SQL Statement',
    database: 'Database',
    minDuration: 'Min Duration',
    maxDuration: 'Max Duration',
    totalCpuTimeLabel: 'Total CPU Time',
    avgDurationLabel: 'Avg Duration',
    error: 'Failed to load slow queries. Please try again.',
    ranges: {
      '1h': 'Last 1 hour',
      '6h': 'Last 6 hours',
      '24h': 'Last 24 hours',
      '7d': 'Last 7 days',
    },
  },
  blocking: {
    title: 'Blocking Processes',
    instance: 'Instance',
    allInstances: 'All instances',
    chainCount: '{count} blocking chain(s)',
    autoRefresh: 'Auto refresh every 30s',
    refreshing: 'Refreshing...',
    noBlocking: 'No blocking processes',
    noBlockingHint: 'System is running normally, no blocking chains detected',
    blocker: 'Blocker',
    blocked: 'Blocked',
    waitType: 'Wait Type',
    waitTime: 'Wait Time',
    hostName: 'Host Name',
    loginName: 'Login Name',
    blockArrow: 'Blocking',
  },
  disk: {
    title: 'Disk Space Monitor',
    instance: 'Instance',
    allInstances: 'All instances',
    collectedAt: 'Collected at:',
    refreshing: 'Refreshing...',
    dbCount: 'Total Databases',
    totalDataFile: 'Data Files (MB)',
    totalLogFile: 'Log Files (MB)',
    totalSize: 'Total Size (MB)',
    totalUsed: 'Used (MB)',
    overallUsage: 'Overall Usage',
    dbUsageTitle: 'Database Space Usage',
    used: 'Used',
    free: 'Free',
    totalLabel: 'Total',
    dbName: 'Database Name',
    dataFile: 'Data File (MB)',
    logFile: 'Log File (MB)',
    usagePct: 'Usage (%)',
    usedMb: 'Used (MB)',
    freeMb: 'Free (MB)',
  },
  indexes: {
    title: 'Index Analysis',
    instance: 'Instance',
    allInstances: 'All instances',
    database: 'Database',
    dbPlaceholder: 'Filter by database name',
    missingIndexes: 'Missing Indexes',
    indexFragments: 'Index Fragments',
    dbName: 'Database',
    schemaName: 'Schema',
    tableName: 'Table',
    equalityColumns: 'Equality Columns',
    includeColumns: 'Include Columns',
    estimatedImpact: 'Est. Impact (%)',
    userSeeks: 'User Seeks',
    userScans: 'User Scans',
    indexName: 'Index Name',
    fragPct: 'Fragmentation (%)',
    pages: 'Pages',
    indexType: 'Index Type',
  },
  report: {
    title: 'System Report',
    instance: 'Instance',
    allInstances: 'All instances',
    timeRange: 'Time Range',
    startEnd: 'Start / End',
    generating: 'Generating...',
    generate: 'Generate Report',
    exportPdf: 'Export PDF',
    exporting: 'Exporting...',
    history: 'History',
    generatingReport: 'Generating report, please wait...',
    regenerate: 'Regenerate',
    reportTitle: 'SQL Monitor · System Performance Report',
    generatedAt: 'Generated:',
    connections: 'Connections',
    ioLatency: 'I/O Latency',
    overview: 'Overview',
    cpuUsage: 'CPU Usage',
    memoryUsage: 'Memory Usage',
    activeConnections: 'Active Connections',
    cacheHitRate: 'Cache Hit Rate',
    deadlockCount: 'Deadlocks',
    slowQueryCount: 'Slow Queries',
    performanceTrend: 'Performance Trend',
    noTrendData: 'No trend data. Please ensure the data collector is running.',
    deadlockAnalysis: 'Deadlock Analysis',
    deadlockNormal: 'Normal',
    deadlockTimes: '{count} total',
    occurTime: 'Occurrence Time',
    victimSession: 'Victim Session ID',
    server: 'Server',
    application: 'Application',
    noDeadlockEvents: 'No deadlock events',
    slowQueryAnalysis: 'Slow Query Analysis',
    avgDurationLabel: 'Avg Duration',
    sqlPreview: 'SQL (first 200 chars)',
    avgDurationMs: 'Avg Duration (ms)',
    noSlowQueryData: 'No slow query data',
    systemStatus: 'System Status',
    blockingProcess: 'Blocking',
    blockingEvents: 'Blocking Events',
    diskSpace: 'Disk Space',
    usageLabel: 'Usage',
    indexStatus: 'Index Status',
    missingIndex: 'Missing Indexes',
    highFragIndex: 'High Fragmentation',
    aiAnalysis: 'AI Analysis & Suggestions',
    historyReports: 'History',
    noHistory: 'No history records',
    ranges: {
      '1h': 'Last 1 hour',
      '6h': 'Last 6 hours',
      '24h': 'Last 24 hours',
      '7d': 'Last 7 days',
      custom: 'Custom',
    },
    pdfTitle: 'SQL Monitor Report - Page {page}',
    pdfFilename: 'SQL_Monitor_Report_',
    generateFailed: 'Failed to generate report. Please try again.',
    exportFailed: 'PDF export failed. Please try again.',
    historyIncomplete: 'Incomplete history data, unable to load.',
    loadHistoryFailed: 'Failed to load history reports.',
  },
  alertRules: {
    title: 'Alert Rules',
    addRule: '+ Add Rule',
    ruleName: 'Rule Name',
    metricCategory: 'Category',
    metricName: 'Metric',
    condition: 'Condition',
    severity: 'Severity',
    notifyMethod: 'Notification',
    status: 'Status',
    noRules: 'No alert rules',
    addTitle: 'Add Alert Rule',
    editTitle: 'Edit Alert Rule',
    namePlaceholder: 'Enter rule name',
    description: 'Description',
    pleaseSelect: 'Select',
    performance: 'Performance',
    memory: 'Memory',
    disk: 'Disk',
    deadlock: 'Deadlock',
    connection: 'Connection',
    metricPlaceholder: 'e.g. cpu_usage',
    operator: 'Operator',
    gt: 'Greater than (gt)',
    lt: 'Less than (lt)',
    gte: 'Greater or equal (gte)',
    lte: 'Less or equal (lte)',
    eq: 'Equal (eq)',
    threshold: 'Threshold',
    cooldown: 'Cooldown (min)',
    email: 'Email',
    dingtalk: 'DingTalk',
    wecom: 'WeCom',
    feishu: 'Feishu',
    silentStart: 'Silent Start',
    silentEnd: 'Silent End',
    nameRequired: 'Please enter a rule name',
    categoryRequired: 'Please select a category',
    metricRequired: 'Please enter a metric name',
    thresholdRequired: 'Please enter a threshold',
    fetchFailed: 'Failed to load alert rules',
    toggleFailed: 'Failed to toggle rule status',
  },
  instances: {
    title: 'Instance Management',
    addInstance: '+ Add Instance',
    instanceName: 'Instance Name',
    serverAddress: 'Server Address',
    port: 'Port',
    connectionStatus: 'Connection Status',
    lastConnectTime: 'Last Connected',
    lastCollectTime: 'Last Collected',
    noInstances: 'No instances',
    testConnection: 'Test Connection',
    addTitle: 'Add Instance',
    editTitle: 'Edit Instance',
    namePlaceholder: 'e.g. Production SQL Server',
    hostAddress: 'Host Address',
    hostPlaceholder: 'e.g. 192.168.1.100',
    username: 'Username',
    usernamePlaceholder: 'SQL Server account',
    password: 'Password',
    passwordPlaceholder: 'Leave empty to keep current',
    database: 'Database',
    dbPlaceholder: 'Default: master',
    enableStatus: 'Status',
    nameRequired: 'Please enter instance name',
    hostRequired: 'Please enter host address',
    connectSuccess: 'Connection successful!',
    connectFailed: 'Connection failed:',
    unknownError: 'Unknown error',
    fetchFailed: 'Failed to load instances',
  },
  auditLogs: {
    title: 'Audit Logs',
    username: 'Username',
    usernamePlaceholder: 'Filter by username',
    operationType: 'Operation Type',
    startTime: 'Start Time',
    endTime: 'End Time',
    user: 'Username',
    operation: 'Operation',
    resource: 'Resource',
    detail: 'Detail',
    ipAddress: 'IP Address',
    operationTime: 'Operation Time',
    noLogs: 'No audit logs',
    fetchFailed: 'Failed to load audit logs. Please try again.',
  },
  settings: {
    title: 'System Settings',
    testConnection: 'Test SQL Server Connection',
    saveAndApply: 'Save & Apply',
    brand: 'Brand Settings',
    systemTitle: 'System Title',
    systemTitleDesc: 'Title displayed on login page and sidebar',
    notifSound: 'Notification Sound',
    notifSoundDesc: 'Play a sound when new notifications arrive',
    logo: 'Logo Image',
    logoDesc: 'Supports PNG, JPG, SVG, WebP. Recommended: 200x50px',
    uploadLogo: 'Upload Logo',
    replaceLogo: 'Replace Logo',
    restoreDefault: 'Restore Default',
    noCustomLogo: 'No custom logo',
    logoUploadSuccess: 'Logo uploaded successfully!',
    logoUploadFailed: 'Logo upload failed:',
    logoRestored: 'Default logo restored',
    logoDeleteFailed: 'Delete failed:',
    system: 'System Settings',
    timezone: 'Timezone',
    timezoneDesc: 'System timezone (used for logs and reports)',
    dataRetention: 'Data Retention (days)',
    dataRetentionDesc: 'Monitoring data older than this will be auto-cleaned (recommended: 90-365 days)',
    frontendUrl: 'Frontend URL',
    frontendUrlDesc: 'Public URL for password reset links etc.',
    sqlServerConfig: 'SQL Server Connection',
    pgConfig: 'PostgreSQL Database',
    collectConfig: 'Data Collection',
    multiInstance: 'Multi-instance Collection',
    multiInstanceDesc: 'When enabled, reads targets from Instance Management. When disabled, uses the SQL Server config above.',
    interval: 'Collection Interval (sec)',
    intervalDesc: 'Data collection frequency (recommended: 30-120 sec)',
    alertConfig: 'Alert Rules Config',
    memoryThreshold: 'Memory Alert Threshold (%)',
    memoryThresholdDesc: 'Trigger alert when SQL Server memory usage exceeds this',
    memoryDuration: 'Memory Alert Duration (min)',
    memoryDurationDesc: 'Alert only if memory exceeds threshold for this duration',
    deadlockAlert: 'Deadlock Alert',
    deadlockAlertDesc: 'Trigger alert notification when deadlock is detected',
    interruptThreshold: 'Collection Interrupt Threshold',
    interruptThresholdDesc: 'Number of consecutive collection failures before alerting',
    cooldown: 'Alert Cooldown (min)',
    cooldownDesc: 'Same alert type will not be sent again within this period',
    recipients: 'Recipient Emails',
    recipientsDesc: 'Alert email recipients, comma-separated',
    notifyChannel: 'Notification Channels',
    wecomChannel: 'WeCom',
    feishuAppChannel: 'Feishu App',
    smtpChannel: 'SMTP Email',
    feishuWebhookChannel: 'Feishu Webhook',
    wecomToggle: 'WeCom Notification',
    wecomToggleDesc: 'Send alerts via WeCom bot',
    wecomWebhook: 'WeCom Webhook URL',
    wecomWebhookDesc: 'WeCom group bot webhook URL',
    feishuAppConfig: 'Feishu App Notification (Critical)',
    feishuAppToggle: 'Feishu App Notification',
    feishuAppToggleDesc: 'Send critical alert notifications via Feishu custom app to specified user',
    feishuAppId: 'App ID',
    feishuAppIdDesc: 'Feishu custom app App ID (starts with cli_)',
    feishuAppSecret: 'App Secret',
    feishuAppSecretDesc: 'Feishu custom app App Secret',
    feishuOpenId: 'Recipient',
    feishuOpenIdDesc: 'Email address or open_id (starts with ou_) of the user who receives notifications',
    feishuSendTest: 'Send Test Message',
    feishuTestFailed: 'Test failed:',
    feishuToggle: 'Feishu Webhook Notification',
    feishuToggleDesc: 'Send alerts via Feishu group bot webhook',
    feishuWebhook: 'Feishu Webhook URL',
    feishuWebhookDesc: 'Feishu group bot webhook URL',
    smtpConfig: 'SMTP Email',
    smtpToggle: 'Email Alert',
    smtpToggleDesc: 'Send alerts and welcome emails via SMTP',
    smtpServer: 'SMTP Server',
    smtpServerDesc: 'SMTP server address',
    smtpPort: 'SMTP Port',
    smtpPortDesc: 'SMTP port (TLS: 587, SSL: 465)',
    smtpUser: 'SMTP Account',
    smtpUserDesc: 'SMTP login / sender email',
    smtpPassword: 'SMTP Password',
    smtpPasswordDesc: 'SMTP password or app authorization code',
    sendTest: 'Send Test Email',
    smtpTestFailed: 'Test failed:',
    unknownResult: 'Unknown result',
    aiConfig: 'AI Model',
    aiProvider: 'AI Provider',
    aiKey: 'API Key',
    aiKeyDesc: '{provider} API key for AI deadlock analysis and reports',
    aiModel: 'AI Model',
    aiModelDesc: 'Select or enter model for AI analysis',
    aiBaseUrl: 'API Base URL',
    aiBaseUrlDesc: 'Custom API URL (must be OpenAI /v1/chat/completions compatible)',
    noConfigChange: 'No configuration changes detected.',
    saveSuccess: 'Saved! {count} config(s) updated, will apply in next collection cycle.',
    saveFailed: 'Save failed:',
    testingConnection: 'Testing connection...',
    testSuccess: 'Connected! SQL Server {host}:{port}',
    testFailed: 'Connection test failed:',
    fillRequired: 'Please fill in server address and credentials',
    connectFailed: 'Connection failed:',
    unknownError: 'Unknown error',
    dbName: 'Database Name',
  },
  users: {
    title: 'User Management',
    addUser: '+ Add User',
    username: 'Username',
    fullName: 'Full Name',
    email: 'Email',
    role: 'Role',
    lastLogin: 'Last Login',
    createTime: 'Created',
    noUsers: 'No users',
    addUserTitle: 'Add User',
    editUserTitle: 'Edit User',
    usernamePlaceholder: '2-50 characters',
    fullNamePlaceholder: 'Optional',
    emailDesc: 'Email for welcome mail and alert notifications',
    password: 'Password',
    resetPassword: 'Reset Password (leave empty to keep)',
    passwordPlaceholder: 'Min 6 characters',
    readOnlyUser: 'Read-only',
    admin: 'Admin',
    superAdmin: 'Super Admin',
    usernameMin: 'Username must be at least 2 characters',
    passwordMin: 'Password must be at least 6 characters',
    newPasswordMin: 'New password must be at least 6 characters',
    confirmDelete: 'Are you sure you want to delete user "{name}"?',
  },
  profile: {
    title: 'Profile',
    basicInfo: 'Basic Info',
    role: 'Role',
    fullName: 'Full Name',
    fullNamePlaceholder: 'Enter full name',
    fullNameHint: 'Displayed in topbar and email notifications',
    email: 'Email',
    emailPlaceholder: 'Enter email address',
    emailHint: 'Used for alert notifications and password reset',
    saveChanges: 'Save Changes',
    changePassword: 'Change Password',
    currentPassword: 'Current Password',
    currentPasswordPlaceholder: 'Enter current password',
    newPassword: 'New Password',
    newPasswordPlaceholder: 'Enter new password (min 6 characters)',
    confirmPassword: 'Confirm New Password',
    confirmPasswordPlaceholder: 'Re-enter new password',
    currentPasswordRequired: 'Please enter current password',
    newPasswordMin: 'New password must be at least 6 characters',
    passwordMismatch: 'Passwords do not match',
    profileUpdated: 'Profile updated',
    saveFailed: 'Save failed',
    passwordChanged: 'Password changed successfully',
    changeFailed: 'Change failed',
    superAdmin: 'Super Admin',
    admin: 'Admin',
    readOnlyUser: 'Read-only',
  },
  help: {
    searchPlaceholder: 'Search help topics...',
    noMatch: 'No matching content found',
    faq: 'FAQ',
    contact: 'Contact Us',
    sections: {
      overview: `<h3>Product Positioning</h3>
      <p>SQL Server Monitoring Platform is an enterprise-level real-time database monitoring and alerting system that helps DBAs and operations teams fully understand the running status of SQL Server instances and quickly identify performance issues.</p>
      <h3>Core Capabilities</h3>
      <ul>
        <li><strong>Real-time Performance Monitoring</strong>: Second-level collection of core metrics such as CPU, memory, disk I/O, and connections</li>
        <li><strong>Deadlock Detection</strong>: Automatically captures deadlock events, showing deadlock graphs and involved sessions</li>
        <li><strong>Slow Query Analysis</strong>: Automatically identifies timing-out SQL statements and provides optimization suggestions</li>
        <li><strong>Blocking Analysis</strong>: Real-time display of blocking chains to quickly locate blocking sources</li>
        <li><strong>Smart Alerts</strong>: Multi-dimensional alert rule configuration with multiple notification methods</li>
        <li><strong>Disk Monitoring</strong>: Tracking data file and log file space usage</li>
        <li><strong>Index Analysis</strong>: Missing and redundant index identification to assist index optimization</li>
        <li><strong>Audit Logs</strong>: Complete recording of user operations and system events</li>
      </ul>
      <h3>Supported Environments</h3>
      <ul>
        <li>SQL Server 2012 / 2014 / 2016 / 2019 / 2022</li>
        <li>Windows Authentication and SQL Server Authentication</li>
        <li>Single instance and Always On availability groups</li>
      </ul>`,
      dashboard: `<h3>Feature Description</h3>
      <p>The dashboard page is the default home page of the system, providing a one-stop view of the overall running status to help you quickly understand the health of all monitored instances.</p>
      <h3>Statistic Cards</h3>
      <ul>
        <li><strong>Total Instances</strong>: Number of configured SQL Server instances</li>
        <li><strong>Online Instances</strong>: Number of instances currently connected and under monitoring</li>
        <li><strong>Active Alerts</strong>: Total number of unresolved alerts</li>
        <li><strong>Critical Alerts</strong>: Number of alerts with "Critical" severity</li>
        <li><strong>Slow Queries</strong>: Total slow queries captured today</li>
        <li><strong>Deadlocks</strong>: Number of deadlock events occurring today</li>
        <li><strong>Average CPU</strong>: Average CPU usage of all online instances</li>
        <li><strong>Average Disk</strong>: Average disk usage of all online instances</li>
        <li><strong>Active Connections</strong>: Total connections across all instances</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li>Click the "Customize" button in the top right to show/hide statistic cards and charts</li>
        <li>Click the time range dropdown to switch between 1h / 6h / 24h / 7d data</li>
        <li>Hover over charts to see values at specific time points</li>
        <li>Click the enlarge icon in the top right of charts for fullscreen view</li>
        <li>Click an instance name in the instance list to jump to its performance trends page</li>
      </ul>`,
      performance: `<h3>Feature Description</h3>
      <p>The performance trends page displays historical curves of various performance metrics in line chart form, helping you analyze performance trends and identify bottlenecks.</p>
      <h3>Monitoring Metrics</h3>
      <ul>
        <li><strong>CPU Usage</strong>: Percentage of CPU used by the SQL Server process</li>
        <li><strong>Memory Usage</strong>: Ratio of SQL Server memory to total server memory</li>
        <li><strong>Disk I/O</strong>: Data file read/write rate (MB/s)</li>
        <li><strong>Connections</strong>: Total current user connections</li>
        <li><strong>Batch Requests</strong>: Batch Requests per second</li>
        <li><strong>Wait Time</strong>: Cumulative wait time for major wait types</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li>Instance selector at the top: switch to view performance data for different instances</li>
        <li>Time range switching: supports 1h / 6h / 24h / 7d / 30d</li>
        <li>Click metric names in the legend to show/hide corresponding curves</li>
        <li>Double-click the chart to reset zoom state</li>
        <li>Hover over curves to see precise time points and values</li>
      </ul>
      <h3>Normal Reference Values</h3>
      <ul>
        <li>CPU usage: Continuous usage above 80% requires attention</li>
        <li>Memory usage: 70%~90% is normal (SQL Server uses as much memory as available)</li>
        <li>Connections: Evaluate based on business scale; sudden growth may indicate connection leaks</li>
      </ul>`,
      deadlocks: `<h3>What is a Deadlock</h3>
      <p>A deadlock occurs when two or more transactions each hold resources that the other needs, causing permanent blocking. SQL Server automatically selects the least costly transaction as a "victim" and rolls it back to break the deadlock.</p>
      <h3>Feature Description</h3>
      <p>The deadlock monitoring page captures and displays all deadlock events in real time, helping you quickly identify deadlock causes and involved SQL statements.</p>
      <h3>Viewing Details</h3>
      <ul>
        <li>Click a deadlock record in the list to expand and view detailed information</li>
        <li><strong>Deadlock Time</strong>: Exact time the deadlock occurred</li>
        <li><strong>Victim Session</strong>: Session ID selected by SQL Server for rollback</li>
        <li><strong>Involved Processes</strong>: Information of all sessions participating in the deadlock</li>
        <li><strong>Deadlock XML</strong>: Original deadlock graph description (copy to SSMS for graphical view)</li>
        <li><strong>Involved Objects</strong>: Database objects involved in the deadlock (tables, indexes, etc.)</li>
      </ul>
      <h3>Common Deadlock Causes and Solutions</h3>
      <ul>
        <li><strong>Inconsistent Access Order</strong>: Different transactions access the same resources in different orders → unify access order</li>
        <li><strong>Long Transactions</strong>: Transactions contain many operations, holding locks for too long → split transactions, shorten execution time</li>
        <li><strong>Coarse Lock Granularity</strong>: Using higher isolation levels or table locks → lower isolation level, optimize indexes</li>
        <li><strong>Missing Indexes</strong>: Queries scan large amounts of data, holding too many row locks → add appropriate indexes</li>
      </ul>`,
      alerts: `<h3>Feature Description</h3>
      <p>The alert management page centrally displays all triggered alert records, supports filtering by level, time, and status, helping you quickly handle important alerts.</p>
      <h3>Alert Levels</h3>
      <ul>
        <li><span style="color:#ff4d4f"><strong>Critical</strong></span>: Affects normal business operation, requires immediate handling (e.g., database unreachable, CPU at 100% continuously)</li>
        <li><span style="color:#fa8c16"><strong>High</strong></span>: Important metric anomaly, needs attention soon (e.g., disk usage above 90%)</li>
        <li><span style="color:#faad14"><strong>Medium</strong></span>: Metric approaching threshold, recommended to monitor (e.g., disk usage above 80%)</li>
        <li><span style="color:#52c41a"><strong>Low</strong></span>: Informational, can be handled when convenient</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li><strong>Filtering</strong>: Click filter conditions at the top to filter alerts by level, time range, and instance</li>
        <li><strong>View Details</strong>: Click an alert record to view detailed metric values, trigger time, and threshold configuration</li>
        <li><strong>Jump to Rule</strong>: Click the alert rule name to jump to the corresponding alert rule configuration page</li>
      </ul>
      <h3>Alert Notification Methods</h3>
      <p>When alerts are triggered, the system notifies via one or more of the following methods according to alert rule configuration:</p>
      <ul>
        <li>System notification (in-app message, bell icon)</li>
        <li>Email notification</li>
        <li>Webhook push (e.g., WeChat Work, DingTalk, Feishu)</li>
        <li>Browser desktop notification (requires enabling in browser)</li>
      </ul>`,
      'slow-queries': `<h3>Feature Description</h3>
      <p>Slow query analysis automatically captures SQL statements exceeding the threshold execution time, helping you identify performance bottlenecks and optimize database query efficiency.</p>
      <h3>Threshold Settings</h3>
      <p>The default slow query threshold is 5 seconds. Administrators can adjust the slow query capture threshold in "System Settings".</p>
      <h3>Operations</h3>
      <ul>
        <li><strong>Filtering</strong>: Filter slow query records by instance, database, and time range</li>
        <li><strong>Sorting</strong>: Click list headers to sort by execution time, CPU time, logical reads, etc.</li>
        <li><strong>View SQL</strong>: Click a record to expand and view the complete SQL text</li>
        <li><strong>Execution Plan</strong>: Click "View Execution Plan" to view the query execution plan XML</li>
      </ul>
      <h3>Key Metrics</h3>
      <ul>
        <li><strong>Execution Time</strong>: Total statement execution time (ms)</li>
        <li><strong>CPU Time</strong>: CPU resources consumed (ms)</li>
        <li><strong>Logical Reads</strong>: Pages read from cache (fewer is better)</li>
        <li><strong>Physical Reads</strong>: Pages read from disk (should be minimized)</li>
        <li><strong>Execution Count</strong>: Number of times the statement was executed</li>
      </ul>
      <h3>Optimization Suggestions</h3>
      <ul>
        <li>Check for missing indexes (refer to missing index suggestions on the "Index Analysis" page)</li>
        <li>Avoid using functions on columns in WHERE conditions, which cause index failure</li>
        <li>Use parameterized queries to improve execution plan reuse</li>
        <li>Use OFFSET/FETCH or cursor-based approaches for large table pagination</li>
      </ul>`,
      blocking: `<h3>What is Blocking</h3>
      <p>Blocking occurs when one transaction holds a lock on a resource while another transaction needs to wait for the lock to be released to continue execution. Moderate blocking is normal, but prolonged blocking leads to performance degradation and application timeouts.</p>
      <h3>Feature Description</h3>
      <p>The blocking process page displays the current blocking chain in real time, presenting the blocker-blocked relationship in a tree structure to help you quickly locate the blocking source.</p>
      <h3>Viewing Blocking Chains</h3>
      <ul>
        <li><strong>Blocker</strong>: Session holding locks and causing other sessions to wait, at the top of the blocking chain</li>
        <li><strong>Blocked</strong>: Session waiting for lock release</li>
        <li><strong>Blocking Chain</strong>: Multi-level blocking relationships (A blocks B, B blocks C)</li>
        <li><strong>Wait Time</strong>: Duration the session has been waiting, shown in red when exceeding threshold</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li>Click the arrow on the left of a blocking session to expand the complete blocking chain</li>
        <li>Click a session ID to view detailed session information (SQL text, login name, host name, etc.)</li>
        <li><strong>KILL Session</strong>: After confirming the blocking source, you can terminate the session (requires admin privileges)</li>
      </ul>
      <h3>Blocking Prevention Suggestions</h3>
      <ul>
        <li>Keep transactions as short as possible to reduce lock hold time</li>
        <li>Ensure queries use appropriate indexes to avoid full table scans producing large numbers of locks</li>
        <li>Use lower transaction isolation levels (e.g., READ COMMITTED SNAPSHOT)</li>
        <li>Control concurrency at the application level to avoid hot resource contention</li>
      </ul>`,
      disk: `<h3>Feature Description</h3>
      <p>The disk space page monitors data file and log file space usage across instances, helping you plan storage capacity in advance and prevent database downtime caused by space exhaustion.</p>
      <h3>Monitoring Content</h3>
      <ul>
        <li><strong>Data Files</strong>: Size, used space, and available space for each database's data files</li>
        <li><strong>Log Files</strong>: Transaction log size and usage rate for each database</li>
        <li><strong>Disk Volumes</strong>: Total and remaining space on disk volumes where database files reside</li>
        <li><strong>Growth Trends</strong>: Space growth curves for the past 7/30 days</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li>Use the instance selector at the top to switch between instances</li>
        <li>Click a database name to expand and view all data file and log file details</li>
        <li>Space usage above 80% is shown in yellow, above 90% in red</li>
      </ul>
      <h3>Common Space Issues and Handling</h3>
      <ul>
        <li><strong>Log File Too Large</strong>: Check if using FULL recovery model without log backups → back up logs regularly or switch to SIMPLE model</li>
        <li><strong>Data File Growing Fast</strong>: Analyze which tables consume the most space → clean historical data, rebuild indexes to release space</li>
        <li><strong>Insufficient Disk Space</strong>: Expand disk volume or migrate some databases to other disks</li>
        <li><strong>tempdb Too Large</strong>: Check if long-running queries are consuming tempdb → optimize queries or add tempdb data files</li>
      </ul>`,
      indexes: `<h3>Feature Description</h3>
      <p>The index analysis page identifies potential performance optimization points by analyzing SQL Server's internal index usage statistics and missing index DMVs, helping you design indexes properly.</p>
      <h3>Missing Index Suggestions</h3>
      <p>SQL Server records scenarios where the query optimizer believes "query performance would be better with this index". The system aggregates and displays these suggestions:</p>
      <ul>
        <li><strong>Database</strong>: Database where the index is suggested</li>
        <li><strong>Table Name</strong>: Table requiring the index</li>
        <li><strong>Equality Columns</strong>: Equality query columns suggested as index keys</li>
        <li><strong>Inequality Columns</strong>: Range query columns suggested as index keys</li>
        <li><strong>Include Columns</strong>: Covering columns suggested as INCLUDE</li>
        <li><strong>Expected Improvement</strong>: User impact percentage (higher means greater potential benefit)</li>
      </ul>
      <h3>Unused Indexes</h3>
      <p>Indexes that have never been used for queries since SQL Server was last started. These indexes consume space and slow down writes. It is recommended to evaluate and delete them:</p>
      <ul>
        <li>Note: Primary keys and unique constraints should not be casually deleted even if unused (they ensure data consistency)</li>
        <li>Note: Index usage statistics accumulate since service restart; they have limited reference value when the runtime is short</li>
      </ul>
      <h3>Index Maintenance Suggestions</h3>
      <ul>
        <li>Fragmentation > 30%: Rebuild index (REBUILD) is recommended</li>
        <li>Fragmentation 5%~30%: Reorganize index (REORGANIZE) is recommended</li>
        <li>Fragmentation < 5%: No maintenance needed</li>
      </ul>
      <h3>Notes</h3>
      <ul>
        <li>Missing index suggestions are for reference only. Evaluate the impact on write performance before creating indexes</li>
        <li>Do not blindly create all suggested indexes. Too many indexes reduce INSERT/UPDATE/DELETE performance</li>
        <li>Validate index effects in a test environment before implementing in production</li>
      </ul.`,
      'alert-rules': `<h3>Feature Description</h3>
      <p>The alert rules page is used to create and manage alert rules, defining "when to trigger alerts" and "how to notify". It is the core configuration of the entire alert system.</p>
      <h3>Rule Components</h3>
      <ul>
        <li><strong>Rule Name</strong>: Identifier name for the rule, suggested to be descriptive (e.g., "CPU usage above 90%")</li>
        <li><strong>Metric Category</strong>: CPU, memory, disk, connections, deadlocks, slow queries, etc.</li>
        <li><strong>Metric Name</strong>: Specific metric item to monitor</li>
        <li><strong>Condition</strong>: Comparison operators (>, >=, <, <=, =) and thresholds</li>
        <li><strong>Duration</strong>: How long the metric must remain abnormal to trigger an alert (avoid transient false positives)</li>
        <li><strong>Severity</strong>: Critical / High / Medium / Low</li>
        <li><strong>Notification Method</strong>: System notification / Email / Webhook</li>
        <li><strong>Target Instances</strong>: Which instances to apply to (all or specific instances)</li>
      </ul.
      <h3>Operations</h3>
      <ul>
        <li><strong>Add Rule</strong>: Click the "+ New Rule" button in the top right</li>
        <li><strong>Enable/Disable</strong>: Click the switch to temporarily disable unneeded rules</li>
        <li><strong>Edit</strong>: Click the edit icon in the operation column to modify rule configuration</li>
        <li><strong>Delete</strong>: Remove rules that are no longer needed</li>
      </ul.
      <h3>Built-in Rules</h3>
      <p>The system has some common alert rules built in, enabled by default after installation:</p>
      <ul>
        <li>Instance connection failure (Critical)</li>
        <li>CPU usage above 90% for 5 minutes (High)</li>
        <li>Disk usage above 90% (High)</li>
        <li>Deadlock occurrence (Medium)</li>
        <li>Slow query above threshold (Medium)</li>
      </ul.`,
      instances: `<h3>Feature Description</h3>
      <p>The instance management page is used to add and manage SQL Server instances to be monitored, which is the foundation of system operation.</p>
      <h3>Adding an Instance</h3>
      <p>Click the "Add Instance" button and fill in the following information:</p>
      <ul>
        <li><strong>Instance Name</strong>: Give the instance a recognizable name (e.g., "Production - Order DB")</li>
        <li><strong>Host Address</strong>: IP or hostname of the server where SQL Server resides</li>
        <li><strong>Port</strong>: SQL Server listening port, default 1433</li>
        <li><strong>Instance Name</strong>: Leave empty for default instance, or fill in instance name for named instances</li>
        <li><strong>Authentication</strong>: SQL Server Authentication or Windows Authentication</li>
        <li><strong>Username/Password</strong>: Database account used for connection</li>
        <li><strong>Database</strong>: Default connected database (optional)</li>
      </ul>
      <h3>Account Permission Requirements</h3>
      <p>For normal collection of monitoring data, the connection account requires the following permissions:</p>
      <ul>
        <li>VIEW SERVER STATE server-level permission</li>
        <li>VIEW ANY DEFINITION server-level permission</li>
        <li>db_datareader role in each database</li>
        <li>SQLAgentReaderRole role in msdb database (if monitoring jobs)</li>
      </ul>.
      <h3>Operations</h3>
      <ul>
        <li><strong>Connection Test</strong>: When adding or editing an instance, click "Test Connection" first to verify configuration</li>
        <li><strong>Enable/Disable</strong>: Temporarily stop monitoring an instance while keeping the configuration</li>
        <li><strong>Status Description</strong>:
          <ul>
            <li><span style="color:#52c41a">Online</span>: Connection normal, monitoring in progress</li>
            <li><span style="color:#ff4d4f">Offline</span>: Connection failed, unable to collect data</li>
            <li><span style="color:#bfbfbf">Disabled</span>: Monitoring manually turned off</li>
          </ul>
        </li>
      </ul.`,
      report: `<h3>Feature Description</h3>
      <p>The system report page is used to generate and export database operation reports, helping you regularly review database health and report operations to management.</p>
      <h3>Report Types</h3>
      <ul>
        <li><strong>Daily Report</strong>: Operation overview for the past 24 hours</li>
        <li><strong>Weekly Report</strong>: Trends and statistics for the past 7 days</li>
        <li><strong>Monthly Report</strong>: Comprehensive analysis for the past 30 days</li>
        <li><strong>Custom</strong>: Freely select time range</li>
      </ul>
      <h3>Report Content</h3>
      <ul>
        <li>Instance health status overview</li>
        <li>Performance metric trend charts (CPU, memory, I/O, connections)</li>
        <li>Alert statistics (by level, by type)</li>
        <li>Top 10 slow queries</li>
        <li>Deadlock event summary</li>
        <li>Disk space change trends</li>
        <li>Index optimization suggestions</li>
      </ul>
      <h3>Operations</h3>
      <ul>
        <li>Select instance and report type, click "Generate Report"</li>
        <li>Reports can be previewed online after generation</li>
        <li>Click "Export PDF" to download as PDF for saving or printing</li>
        <li>Click "Save as Image" to export individual charts as PNG</li>
      </ul>`,
      settings: `<h3>Brand Settings</h3>
      <ul>
        <li><strong>System Name</strong>: Platform name displayed on login page and sidebar top</li>
        <li><strong>Logo Icon</strong>: Upload a custom Logo image</li>
        <li><strong>Theme Color</strong>: Custom system theme color (current supports light/dark mode switching)</li>
      </ul>
      <h3>Alert Configuration</h3>
      <ul>
        <li><strong>Collection Frequency</strong>: Performance data collection interval (default 30 seconds)</li>
        <li><strong>Data Retention Days</strong>: Monitoring data retention duration (default 30 days)</li>
        <li><strong>Alert Silence Period</strong>: Minimum interval before the same alert triggers again</li>
        <li><strong>Slow Query Threshold</strong>: Execution time threshold for slow query capture (default 5 seconds)</li>
      </ul>
      <h3>Notification Channels</h3>
      <ul>
        <li><strong>Email Notification</strong>: Configure SMTP server info, supports alert email push</li>
        <li><strong>Webhook</strong>: Configure bot Webhook addresses for WeChat Work, DingTalk, Feishu, etc.</li>
        <li>Click "Test Send" after configuration to verify settings</li>
      </ul>
      <h3>Notes</h3>
      <ul>
        <li>Changing collection frequency affects data precision and storage. Higher frequency means more precise data but larger storage</li>
        <li>Data is automatically cleaned up after the retention period expires. Export important reports in advance</li>
        <li>After changing email and Webhook configurations, always test and verify</li>
      </ul>`,
      users: `<h3>Feature Description</h3>
      <p>The user management page allows administrators to create and manage system accounts, assign different permission roles, and ensure secure system usage.</p>
      <h3>Role Description</h3>
      <table style="width:100%;border-collapse:collapse;margin:12px 0;">
        <thead>
          <tr style="background:var(--bg-hover);">
            <th style="padding:8px 12px;border:1px solid var(--border-color);text-align:left;">Role</th>
            <th style="padding:8px 12px;border:1px solid var(--border-color);text-align:left;">Permission Scope</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>Super Administrator</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">Has all permissions, including user management, system settings, instance management, etc.</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>Administrator</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">Can configure alert rules and manage instances, but cannot manage users or modify core system settings</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>Viewer</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">Read-only permissions, can view all monitoring data and alerts but cannot make any configuration changes</td>
          </tr>
        </tbody>
      </table>
      <h3>Operations</h3>
      <ul>
        <li><strong>Add User</strong>: Click "Add User", fill in username, name, email, role, initial password</li>
        <li><strong>Reset Password</strong>: Click the key icon in the operation column to reset the user's password</li>
        <li><strong>Enable/Disable</strong>: Users cannot log in after being disabled</li>
        <li><strong>Edit</strong>: Modify the user's name, email, role, and other information</li>
      </ul>
      <h3>Security Recommendations</h3>
      <ul>
        <li>Follow the principle of least privilege, only grant necessary roles</li>
        <li>Regularly audit the user list and clean up accounts of departing employees</li>
        <li>Set initial passwords as strong passwords and require users to change them on first login</li>
        <li>Important operations are recorded in audit logs, viewable on the "Audit Logs" page</li>
      </ul.`,
      faq: `<h3>Q: What to do when connection fails when adding an instance?</h3>
      <p>A: Please follow these steps to troubleshoot:</p>
      <ol>
        <li>Confirm the host address and port are correct, and the network is reachable (ping or telnet test)</li>
        <li>Confirm SQL Server has TCP/IP protocol enabled (check in SQL Server Configuration Manager)</li>
        <li>Confirm the firewall has allowed the SQL Server port (default 1433)</li>
        <li>Confirm the account password is correct and the account has sufficient permissions (VIEW SERVER STATE, etc.)</li>
        <li>If it is a named instance, confirm the SQL Server Browser service is started</li>
      </ol>
      <h3>Q: Why are alerts triggered but no notification received?</h3>
      <p>A: Please check the following:</p>
      <ol>
        <li>Confirm the notification method in the alert rule is checked</li>
        <li>If email notification, check the SMTP configuration in "System Settings → Notification Channels"</li>
        <li>If Webhook, verify the Webhook address is valid and the bot is in the group</li>
        <li>Check if within the alert silence period, repeated alerts may be suppressed</li>
        <li>Check if notifications are going to spam or being blocked</li>
      </ol>
      <h3>Q: What to do if monitoring data is not updating?</h3>
      <p>A: Possible causes and solutions:</p>
      <ol>
        <li>Check if the instance status is "Online", collection cannot happen if offline</li>
        <li>Check if the backend service is running normally</li>
        <li>Try manually refreshing the page to rule out browser cache issues</li>
        <li>Check the backend logs for error messages</li>
      </ol>
      <h3>Q: What to do if I forgot my login password?</h3>
      <p>A:</p>
      <ul>
        <li>If the system has email service configured, click "Forgot Password" on the login page to reset via email</li>
        <li>If you are an administrator and cannot reset via email, contact a super administrator to reset in user management</li>
        <li>If even the sole super administrator has forgotten, direct database modification or re-initialization is required</li>
      </ul>
      <h3>Q: How to enable dark mode?</h3>
      <p>A: Click the moon/sun icon in the top right of the page to switch between light and dark modes. The system will remember your choice.</p>
      <h3>Q: How to upgrade the system to a new version?</h3>
      <p>A: When the system detects a new version, a yellow dot appears next to the version number at the bottom of the sidebar and top bar. Click to view update notes. Upgrade steps:</p>
      <ol>
        <li>Back up the database and configuration files</li>
        <li>Pull the latest code (git pull)</li>
        <li>Rebuild the Docker image and start</li>
      </ol>
      <h3>Q: How many instances can be monitored?</h3>
      <p>A: Theoretically there is no upper limit, but it is recommended not to exceed 50 SQL Server instances for a single-instance deployment. If exceeding 50, pay attention to the resource usage of the backend server and consider horizontal scaling if necessary.</p>`,
      contact: `<h3>Technical Support</h3>
      <p>If you encounter problems during use, you can contact us through the following methods:</p>
      <ul>
        <li><strong>Department</strong>: Sun Valley IT Department</li>
        <li><strong>Email</strong>: Contact the IT support email</li>
        <li><strong>WeChat Work</strong>: Search for the IT support group</li>
      </ul>
      <h3>Feedback</h3>
      <p>We highly value your feedback. If you have feature suggestions, usage experience, or find bugs, please feel free to provide feedback:</p>
      <ul>
        <li>Clearly describe the problem encountered or the suggested feature</li>
        <li>If it is a bug, please attach screenshots and operation steps</li>
        <li>Provide environment information such as browser and system version used</li>
      </ul>
      <h3>Version Information</h3>
      <p>Check the sidebar bottom or top bar for the current version number. Click the version number to check if a new version is available.</p>`,
    },
  },
  login: {
    slogan: 'Real-time Monitoring · Smart Alerts · Deep Analysis',
    feature1: 'Full-stack Performance Monitoring',
    feature2: 'Smart Alerts & Multi-channel Notifications',
    feature3: 'AI-powered Analysis Reports',
    copyright: 'Sun Valley IT Dept',
    welcome: 'Welcome',
    subtitle: 'Sign in with your account',
    username: 'Username',
    usernamePlaceholder: 'Enter username',
    password: 'Password',
    passwordPlaceholder: 'Enter password',
    forgotPassword: 'Forgot password?',
    loginButton: 'Sign In',
    logging: 'Signing in...',
    loginFailed: 'Login failed. Please try again.',
  },
  forgotPassword: {
    title: 'Forgot Password',
    subtitle: 'Enter your registered email and we will send a verification code',
    email: 'Email Address',
    emailPlaceholder: 'Enter registered email',
    sending: 'Sending...',
    sendCode: 'Send Code',
    rememberPassword: 'Remember your password?',
    backToLogin: 'Back to Login',
    resetTitle: 'Reset Password',
    codeSentTo: 'Code sent to',
    code: 'Verification Code',
    codePlaceholder: 'Enter 6-digit code',
    resend: 'Resend',
    newPassword: 'New Password',
    newPasswordPlaceholder: 'Enter new password (min 6 characters)',
    confirmPassword: 'Confirm Password',
    confirmPasswordPlaceholder: 'Re-enter new password',
    resetting: 'Resetting...',
    confirmReset: 'Confirm Reset',
    backToPrev: 'Back',
    resetSuccess: 'Password Reset Successful',
    resetSuccessDesc1: 'Your password has been successfully reset.',
    resetSuccessDesc2: 'Please sign in with your new password.',
    loginNow: 'Sign In Now',
    sendFailed: 'Failed to send. Please try again.',
    codeRequired: 'Please enter the 6-digit code',
    passwordMin: 'Password must be at least 6 characters',
    passwordMismatch: 'Passwords do not match',
    resetFailed: 'Reset failed. Please try again.',
  },
  setup: {
    platformTitle: 'SQL Monitor',
    platformDesc: 'Database Query Performance Monitoring & Analysis',
    welcomeTitle: 'Welcome to SQL Monitor',
    welcomeDesc1: 'This system helps you monitor SQL Server database performance in real-time,',
    welcomeDesc2: 'detect deadlocks, analyze slow queries, manage alert notifications,',
    welcomeDesc3: 'and provides AI-powered analysis and report generation.',
    feature1: 'Real-time Performance Monitoring',
    feature2: 'Smart Alerts & Multi-channel Notifications (Email, WeCom)',
    feature3: 'AI-powered Deadlock Analysis & System Reports',
    feature4: 'Multi SQL Server Instance Management',
    startInstall: 'Start Installation',
    createAdmin: 'Create Super Admin',
    createAdminDesc: 'Set up the super admin account for first login and system management',
    username: 'Username',
    usernamePlaceholder: 'Enter admin username',
    displayName: 'Display Name',
    displayNamePlaceholder: 'Enter display name (optional)',
    password: 'Password',
    passwordPlaceholder: 'Enter password',
    confirmPassword: 'Confirm Password',
    confirmPasswordPlaceholder: 'Re-enter password',
    prevStep: 'Previous',
    creating: 'Creating...',
    createAndContinue: 'Create & Continue',
    basicConfig: 'Basic Configuration',
    basicConfigDesc: 'Configure timezone and data retention policy',
    timezone: 'Timezone',
    timezoneDesc: 'Used for log and report timestamps',
    beijing: 'Beijing (UTC+8)',
    tokyo: 'Tokyo (UTC+9)',
    newyork: 'New York (UTC-5)',
    losangeles: 'Los Angeles (UTC-8)',
    london: 'London (UTC+0)',
    dataRetention: 'Data Retention (days)',
    dataRetentionDesc: 'Monitoring data older than this will be auto-cleaned (recommended: 90-365 days)',
    saving: 'Saving...',
    saveAndFinish: 'Save & Finish',
    installComplete: 'Installation Complete!',
    completeDesc1: 'System initialization is complete.',
    completeDesc2: 'You can now sign in with the super admin account you just created.',
    adminAccount: 'Admin Account',
    adminTimeZone: 'Timezone',
    dataRetentionLabel: 'Data Retention',
    loginNow: 'Sign In Now',
    steps: {
      welcome: 'Welcome',
      intro: 'Introduction',
      admin: 'Admin',
      createAccount: 'Create Account',
      config: 'Config',
      systemSettings: 'Settings',
      complete: 'Complete',
      installComplete: 'Done',
    },
    usernameRequired: 'Please enter username',
    usernameMin: 'Username must be at least 2 characters',
    passwordRequired: 'Please enter password',
    passwordMin: 'Password must be at least 6 characters',
    confirmRequired: 'Please confirm password',
    passwordMismatch: 'Passwords do not match',
    createAdminFailed: 'Failed to create admin',
    saveConfigFailed: 'Failed to save configuration',
  },
  aiAssistant: {
    title: 'AI Assistant',
    subtitle: 'Let AI plan and execute tasks automatically',
    newTask: '+ New Task',
    inputPlaceholder: 'Describe the task you want to execute, e.g.: Analyze database health...',
    sending: 'Analyzing...',
    planGenerated: 'Plan generated, {count} step(s)',
    taskCompleted: 'Task completed',
    taskRunning: 'Running...',
    taskFailed: 'Failed',
    taskPending: 'Pending',
    stepRunning: 'Running...',
    stepCompleted: 'Completed',
    stepFailed: 'Failed',
    stepPending: 'Pending',
    noTasks: 'No tasks',
    noTasksHint: 'Click the button above to create a new task',
    deleteTask: 'Delete task',
    confirmDelete: 'Are you sure you want to delete this task?',
    noResult: 'No analysis result yet',
    fetchFailed: 'Failed to load tasks',
    createFailed: 'Failed to create task',
    deleteFailed: 'Failed to delete task',
    followUpPlaceholder: 'Ask a follow-up question based on the analysis...',
    followUpFailed: 'Follow-up failed',
    userMessage: 'User',
    aiResponse: 'AI Assistant',
    stepResult: 'Step Result',
    followUp: 'Follow-up',
    taskPlanning: 'Thinking / Task Planning',
    diagnosticReport: 'Diagnostic Report',
    generatingReport: 'Generating report...',
    taskAwaitingReport: 'Awaiting report',
  },
}
