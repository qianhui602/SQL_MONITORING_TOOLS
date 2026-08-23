export default {
  common: {
    query: '查询',
    search: '搜索',
    reset: '重置',
    confirm: '确定',
    cancel: '取消',
    delete: '删除',
    edit: '编辑',
    save: '保存',
    loading: '加载中...',
    empty: '暂无数据',
    retry: '重试',
    refresh: '刷新',
    total: '共',
    items: '条',
    page: '页',
    perPage: '每页',
    prevPage: '上一页',
    nextPage: '下一页',
    pageInfo: '第 {page} / {total} 页',
    all: '全部',
    enable: '启用',
    disable: '禁用',
    enabled: '已开启',
    disabled: '已关闭',
    submit: '提交中...',
    optional: '可选',
    seconds: '秒',
    minutes: '分',
    hours: '小时',
    day: '天',
    online: '在线',
    offline: '离线',
    disabledStatus: '已禁用',
    connectError: '连接异常',
    operationFailed: '操作失败',
    deleteFailed: '删除失败',
    confirmDelete: '确定要删除"{name}"吗？',
    serverAddress: '服务器地址',
    port: '端口',
    account: '账号',
    password: '密码',
    database: '数据库',
    operation: '操作',
  },
  layout: {
    version: '版本',
    notifications: '通知',
    markAllRead: '全部已读',
    noNotifications: '暂无通知',
    soundReminder: '声音提醒',
    desktopNotification: '桌面通知',
    switchToDark: '切换到暗色模式',
    switchToLight: '切换到浅色模式',
    personalSettings: '个人设置',
    logout: '退出登录',
    closeOthers: '关闭其他',
    closeCurrent: '关闭当前',
    closeAll: '关闭全部',
    newVersion: '发现新版本 v{version}',
    viewUpgradeGuide: '查看升级指南',
    later: '稍后再说',
    copyright: '太阳谷信息技术部 2026',
    menu: {
      dashboard: '总览',
      trends: '性能趋势',
      deadlocks: '死锁监控',
      alerts: '告警管理',
      slowQueries: '慢查询分析',
      blocking: '阻塞进程',
      disk: '磁盘空间',
      indexes: '索引分析',
      report: '系统报告',
      alertRules: '告警规则',
      instances: '实例管理',
      auditLogs: '审计日志',
      settings: '系统设置',
      users: '用户管理',
      help: '帮助',
      aiAssistant: 'AI 助手',
    },
    langSwitch: {
      'zh-CN': '中文',
      'en-US': 'English',
    },
  },
  dashboard: {
    statCards: {
      cpu: 'CPU 使用率',
      memory: '内存使用量',
      connections: '活跃连接',
      cache: '缓存命中率',
      disk: '磁盘使用率',
      batch: '批处理/秒',
      locks: '锁等待',
      deadlock: '死锁事件',
      instances: '数据库实例',
    },
    noInstances: '无实例',
    dbStatus: '数据库连接状态',
    allInstances: '所有实例',
    instanceSelect: '所有实例',
    timeRange: '时间范围',
    refresh: '刷新',
    compare: '对比',
    customize: '自定义',
    sort: '排序',
    statCardsTitle: '统计卡片',
    chartsTitle: '图表',
    chartSort: '图表排序（点击箭头调整位置）',
    resetChartOrder: '恢复默认排序',
    compareYesterday: '昨天此时',
    compareLastWeek: '上周此时',
    compareLastMonth: '上月此时',
    charts: {
      cpu: 'CPU 使用率趋势',
      memory: '内存使用趋势',
      connections: '连接数趋势',
      io: 'IO 延迟趋势',
      locks: '锁等待趋势',
      batch: '批处理请求趋势',
    },
    ranges: {
      '1h': '最近 1 小时',
      '6h': '最近 6 小时',
      '24h': '最近 24 小时',
      '7d': '最近 7 天',
    },
    refreshOptions: {
      '5s': '5 秒',
      '10s': '10 秒',
      '30s': '30 秒',
      '60s': '60 秒',
      off: '关闭',
    },
    details: '查看详情',
    chartDetail: '图表详情',
    dragSort: '拖拽排序',
    customLayoutSort: '自定义布局排序',
    moveUp: '上移',
    moveDown: '下移',
    series: {
      cpuUsage: 'CPU 使用率',
      memoryUsage: '内存使用量',
      activeConnections: '活跃连接数',
      ioReadLatency: '读延迟',
      ioWriteLatency: '写延迟',
      lockWaits: '锁等待数',
      batchRequests: '批处理请求/秒',
    },
    previousPeriod: '上一周期',
  },
  trends: {
    instance: '实例',
    allInstances: '全部实例',
    metricCategory: '指标分类',
    timeRange: '时间范围',
    metricName: '指标名称',
    categories: {
      cpu: 'CPU',
      memory: '内存',
      connections: '连接数',
      io: 'IO',
      locks: '锁等待',
      batch_requests: '批处理请求',
    },
    metrics: {
      cpu_usage: 'CPU 使用率',
      sql_cpu: 'SQL CPU 占用',
      sql_server_memory_mb: '内存使用量(MB)',
      buffer_cache_hit_ratio: '缓存命中率',
      target_memory_mb: '目标内存(MB)',
      page_life_expectancy: '页生命周期',
      total_connections: '总连接数',
      active_sessions: '活跃会话',
      user_connections: '用户连接',
      user_processes: '用户进程',
      avg_read_latency_ms: '读延迟(ms)',
      avg_write_latency_ms: '写延迟(ms)',
      total_reads: '总读取次数',
      total_writes: '总写入次数',
      read_mb: '读取MB',
      write_mb: '写入MB',
      waiting_locks: '等待锁数量',
      lock_waits: '锁等待数',
      avg_lock_wait_ms: '平均锁等待(ms)',
      batch_requests_sec: '批处理请求/秒',
      sql_compilations_sec: 'SQL编译/秒',
      sql_recompilations_sec: 'SQL重编译/秒',
    },
  },
  deadlocks: {
    instance: '实例',
    allInstances: '全部实例',
    startTime: '开始时间',
    endTime: '结束时间',
    user: '用户',
    host: '主机（设备）',
    application: '应用程序',
    userPlaceholder: '用户名，如 Sboadmin',
    hostPlaceholder: '主机名，如 MSSAP01C',
    appPlaceholder: '应用名，如 SAP Business One',
    occurTime: '发生时间',
    victimSessionId: '受害会话 ID',
    serverAddress: 'SQL Server 地址',
    relatedSql: '关联 SQL 语句',
    session: '会话',
    userLabel: '用户:',
    hostLabel: '主机:',
    appLabel: '应用:',
    isolationLabel: '隔离:',
    involvedObjects: '涉及对象',
    aiAnalysis: 'DeepSeek AI 分析',
    aiButton: 'AI 分析',
    analyzing: '分析中...',
    aiHint: '点击「AI 分析」按钮调用 DeepSeek 大模型分析死锁原因',
    rawXml: '原始死锁 XML',
    noData: '无',
    error: '获取死锁列表失败，请稍后重试',
    fetchFailed: '获取死锁列表失败',
  },
  alerts: {
    severity: '严重级别',
    startTime: '开始时间',
    endTime: '结束时间',
    alertType: '告警类型',
    message: '消息',
    triggerTime: '触发时间',
  },
  slowQueries: {
    instance: '实例',
    allInstances: '全部实例',
    timeRange: '时间范围',
    queryText: '查询文本',
    execCount: '执行次数',
    totalCpuTime: '总CPU时间(ms)',
    totalLogicalReads: '总逻辑读',
    avgDuration: '平均耗时(ms)',
    lastExecTime: '最后执行时间',
    collectedAt: '采集时间',
    fullSql: '完整 SQL 语句',
    database: '数据库',
    minDuration: '最小耗时',
    maxDuration: '最大耗时',
    error: '获取慢查询列表失败，请稍后重试',
    ranges: {
      '1h': '最近1小时',
      '6h': '最近6小时',
      '24h': '最近24小时',
      '7d': '最近7天',
    },
  },
  blocking: {
    title: '阻塞进程',
    instance: '实例',
    allInstances: '全部实例',
    chainCount: '共 {count} 个阻塞链',
    autoRefresh: '每30秒自动刷新',
    refreshing: '刷新中...',
    noBlocking: '当前无阻塞进程',
    noBlockingHint: '系统运行正常，没有检测到阻塞链',
    blocker: '阻塞者',
    blocked: '被阻塞',
    waitType: '等待类型',
    waitTime: '等待时间',
    hostName: '主机名',
    loginName: '登录名',
    blockArrow: '阻塞',
  },
  disk: {
    title: '磁盘空间监控',
    instance: '实例',
    allInstances: '全部实例',
    collectedAt: '采集时间:',
    refreshing: '刷新中...',
    dbCount: '数据库总数',
    totalDataFile: '总数据文件(MB)',
    totalLogFile: '总日志文件(MB)',
    totalSize: '总大小(MB)',
    totalUsed: '总已用(MB)',
    overallUsage: '总体使用率',
    dbUsageTitle: '各数据库空间使用率',
    used: '已用',
    free: '可用',
    totalLabel: '总计',
    dbName: '数据库名',
    dataFile: '数据文件(MB)',
    logFile: '日志文件(MB)',
    usagePct: '使用率(%)',
  },
  indexes: {
    title: '索引分析',
    instance: '实例',
    allInstances: '全部实例',
    database: '数据库',
    dbPlaceholder: '输入数据库名筛选',
    missingIndexes: '缺失索引',
    indexFragments: '索引碎片',
    dbName: '数据库名',
    schemaName: '架构名',
    tableName: '表名',
    equalityColumns: '相等列',
    includeColumns: '包含列',
    estimatedImpact: '预估影响(%)',
    userSeeks: '用户查找次数',
    userScans: '用户扫描次数',
    indexName: '索引名',
    fragPct: '碎片率(%)',
    pages: '页数',
    indexType: '索引类型',
  },
  report: {
    title: '系统报告',
    instance: '实例',
    allInstances: '所有实例',
    timeRange: '时间范围',
    startEnd: '起止',
    generating: '生成中...',
    generate: '生成报告',
    exportPdf: '导出PDF',
    exporting: '导出中...',
    history: '历史记录',
    generatingReport: '正在生成报告，请稍候...',
    regenerate: '重新生成',
    reportTitle: 'SQL 监控平台 · 系统性能分析报告',
    generatedAt: '生成时间：',
    connections: '连接数',
    ioLatency: 'I/O 延迟',
    overview: '概览摘要',
    cpuUsage: 'CPU 使用率',
    memoryUsage: '内存使用',
    activeConnections: '活跃连接',
    cacheHitRate: '缓存命中率',
    deadlockCount: '死锁次数',
    slowQueryCount: '慢查询数',
    performanceTrend: '性能趋势',
    noTrendData: '暂无性能趋势数据，请确保监控数据采集任务已启动',
    deadlockAnalysis: '死锁分析',
    deadlockNormal: '正常',
    deadlockTimes: '共 {count} 次',
    occurTime: '发生时间',
    victimSession: '受害会话ID',
    server: '服务器',
    application: '应用程序',
    noDeadlockEvents: '无死锁事件',
    slowQueryAnalysis: '慢查询分析',
    avgDurationLabel: '平均耗时',
    sqlPreview: 'SQL（前200字符）',
    avgDurationMs: '平均耗时(ms)',
    noSlowQueryData: '无慢查询数据',
    systemStatus: '系统状态',
    blockingProcess: '阻塞进程',
    blockingEvents: '阻塞事件数',
    diskSpace: '磁盘空间',
    usageLabel: '使用率',
    indexStatus: '索引状况',
    missingIndex: '缺失索引',
    highFragIndex: '高碎片索引',
    aiAnalysis: 'AI 分析与建议',
    historyReports: '历史报告',
    noHistory: '暂无历史记录',
    ranges: {
      '1h': '最近1小时',
      '6h': '最近6小时',
      '24h': '最近24小时',
      '7d': '最近7天',
      custom: '自定义',
    },
    pdfTitle: 'SQL 监控平台报告 - 第 {page} 页',
    pdfFilename: 'SQL监控报告_',
    generateFailed: '生成报告失败，请稍后重试',
    exportFailed: 'PDF 导出失败，请重试',
    historyIncomplete: '历史报告数据不完整，无法加载',
    loadHistoryFailed: '加载历史报告失败',
  },
  alertRules: {
    title: '告警规则管理',
    addRule: '+ 新增规则',
    ruleName: '规则名称',
    metricCategory: '指标分类',
    metricName: '指标名',
    condition: '条件',
    severity: '严重级别',
    notifyMethod: '通知方式',
    status: '状态',
    noRules: '暂无告警规则',
    addTitle: '新增告警规则',
    editTitle: '编辑告警规则',
    namePlaceholder: '输入规则名称',
    description: '描述',
    pleaseSelect: '请选择',
    performance: '性能',
    memory: '内存',
    disk: '磁盘',
    deadlock: '死锁',
    connection: '连接',
    metricPlaceholder: '如 cpu_usage',
    operator: '运算符',
    gt: '大于 (gt)',
    lt: '小于 (lt)',
    gte: '大于等于 (gte)',
    lte: '小于等于 (lte)',
    eq: '等于 (eq)',
    threshold: '阈值',
    cooldown: '冷却期(分钟)',
    email: '邮件',
    dingtalk: '钉钉',
    wecom: '企业微信',
    feishu: '飞书',
    silentStart: '静默开始时间',
    silentEnd: '静默结束时间',
    nameRequired: '请输入规则名称',
    categoryRequired: '请选择指标分类',
    metricRequired: '请输入指标名',
    thresholdRequired: '请输入阈值',
    fetchFailed: '获取告警规则失败',
    toggleFailed: '切换规则状态失败',
  },
  instances: {
    title: '实例管理',
    addInstance: '+ 添加实例',
    instanceName: '实例名称',
    serverAddress: '服务器地址',
    port: '端口',
    connectionStatus: '连接状态',
    lastConnectTime: '最后连接时间',
    lastCollectTime: '最后采集时间',
    noInstances: '暂无实例',
    testConnection: '测试连接',
    addTitle: '添加实例',
    editTitle: '编辑实例',
    namePlaceholder: '例如：生产环境SQL Server',
    hostAddress: '主机地址',
    hostPlaceholder: '例如：192.168.1.100',
    username: '用户名',
    usernamePlaceholder: 'SQL Server 账号',
    password: '密码',
    passwordPlaceholder: '留空则不修改',
    database: '数据库',
    dbPlaceholder: '默认 master',
    enableStatus: '启用状态',
    nameRequired: '请输入实例名称',
    hostRequired: '请输入主机地址',
    connectSuccess: '连接成功！',
    connectFailed: '连接失败:',
    unknownError: '未知错误',
    fetchFailed: '获取实例列表失败',
  },
  auditLogs: {
    title: '审计日志',
    username: '用户名',
    usernamePlaceholder: '输入用户名筛选',
    operationType: '操作类型',
    startTime: '开始时间',
    endTime: '结束时间',
    user: '用户名',
    operation: '操作',
    resource: '资源',
    detail: '详情',
    ipAddress: 'IP 地址',
    operationTime: '操作时间',
    noLogs: '暂无审计日志',
    fetchFailed: '获取审计日志失败，请稍后重试',
  },
  settings: {
    title: '系统配置',
    testConnection: '测试 SQL Server 连接',
    saveAndApply: '保存并应用',
    brand: '品牌设置',
    systemTitle: '系统标题',
    systemTitleDesc: '登录页和侧边栏显示的系统标题',
    notifSound: '通知声音',
    notifSoundDesc: '有新通知时播放提示音',
    logo: 'Logo 图片',
    logoDesc: '支持 PNG、JPG、SVG、WebP，建议尺寸 200x50px',
    uploadLogo: '上传 Logo',
    replaceLogo: '更换 Logo',
    restoreDefault: '恢复默认',
    noCustomLogo: '暂无自定义 Logo',
    logoUploadSuccess: 'Logo 上传成功！',
    logoUploadFailed: 'Logo 上传失败:',
    logoRestored: '已恢复默认 Logo',
    logoDeleteFailed: '删除失败:',
    system: '系统设置',
    timezone: '系统时区',
    timezoneDesc: '系统时区（用于日志和报表时间显示）',
    dataRetention: '数据保留天数',
    dataRetentionDesc: '超过此天数的监控数据将被自动清理（建议 90-365 天）',
    frontendUrl: '前端访问地址',
    frontendUrlDesc: '系统对外访问地址，用于密码重置邮件等链接生成',
    sqlServerConfig: 'SQL Server 连接配置',
    pgConfig: 'PostgreSQL 后台数据库',
    collectConfig: '数据采集配置',
    multiInstance: '启用多实例采集',
    multiInstanceDesc: '开启后从「实例管理」读取监控目标列表，关闭则使用上方 SQL Server 配置',
    interval: '采集间隔（秒）',
    intervalDesc: '数据采集频率，建议 30-120 秒',
    alertConfig: '告警规则配置',
    memoryThreshold: '内存告警阈值（%）',
    memoryThresholdDesc: 'SQL Server 内存使用率超过此值触发告警',
    memoryDuration: '内存告警持续时长（分钟）',
    memoryDurationDesc: '内存持续超过阈值超过此时长才触发告警',
    deadlockAlert: '死锁告警开关',
    deadlockAlertDesc: '检测到死锁事件时是否触发告警通知',
    interruptThreshold: '采集中断阈值（次）',
    interruptThresholdDesc: '连续多少次采集失败后触发中断告警',
    cooldown: '告警冷却期（分钟）',
    cooldownDesc: '相同类型告警在此期间不重复发送',
    recipients: '收件人邮箱',
    recipientsDesc: '告警邮件接收人，多个用逗号分隔',
    notifyChannel: '通知渠道配置',
    wecomToggle: '企业微信通知开关',
    wecomToggleDesc: '是否通过企业微信机器人发送告警通知',
    wecomWebhook: '企业微信 Webhook URL',
    wecomWebhookDesc: '企业微信群机器人 Webhook 地址',
    feishuAppConfig: '飞书应用通知（关键错误）',
    feishuAppToggle: '飞书应用通知开关',
    feishuAppToggleDesc: '通过飞书自建应用给指定用户发送关键错误（严重告警）通知',
    feishuAppId: 'App ID',
    feishuAppIdDesc: '飞书自建应用的 App ID（以 cli_ 开头）',
    feishuAppSecret: 'App Secret',
    feishuAppSecretDesc: '飞书自建应用的 App Secret（应用密钥）',
    feishuOpenId: '接收人 open_id',
    feishuOpenIdDesc: '接收通知用户的 open_id（以 ou_ 开头）',
    feishuSendTest: '发送测试消息',
    feishuTestFailed: '测试失败:',
    smtpConfig: 'SMTP 邮件配置',
    smtpToggle: '邮件告警开关',
    smtpToggleDesc: '是否通过邮件发送告警通知和欢迎邮件',
    smtpServer: 'SMTP 服务器',
    smtpServerDesc: 'SMTP 服务器地址',
    smtpPort: 'SMTP 端口',
    smtpPortDesc: 'SMTP 端口（TLS 用 587，SSL 用 465）',
    smtpUser: '发件人账号',
    smtpUserDesc: 'SMTP 登录账号 / 发件人邮箱',
    smtpPassword: '发件人密码',
    smtpPasswordDesc: 'SMTP 登录密码或应用授权码',
    sendTest: '发送测试邮件',
    smtpTestFailed: '测试失败:',
    unknownResult: '未知结果',
    aiConfig: 'AI 模型配置',
    aiProvider: 'AI 提供商',
    aiKey: 'API 密钥',
    aiKeyDesc: '{provider} API 密钥，用于 AI 死锁分析和报告生成',
    aiModel: 'AI 模型',
    aiModelDesc: '选择或输入用于 AI 分析的模型',
    aiBaseUrl: 'API Base URL',
    aiBaseUrlDesc: '自定义 API 地址（需兼容 OpenAI /v1/chat/completions 接口）',
    noConfigChange: '没有检测到配置变更。',
    saveSuccess: '保存成功！已更新 {count} 项配置，将在下一个采集周期自动应用。',
    saveFailed: '保存失败:',
    testingConnection: '正在测试连接...',
    testSuccess: '连接成功！SQL Server {host}:{port}',
    testFailed: '测试连接失败:',
    fillRequired: '请填写服务器地址和账号',
    connectFailed: '连接失败:',
    unknownError: '未知错误',
    dbName: '数据库名',
  },
  users: {
    title: '用户管理',
    addUser: '+ 新建用户',
    username: '用户名',
    fullName: '姓名',
    email: '邮箱',
    role: '角色',
    lastLogin: '最后登录',
    createTime: '创建时间',
    noUsers: '暂无用户',
    addUserTitle: '新建用户',
    editUserTitle: '编辑用户',
    usernamePlaceholder: '2-50 字符',
    fullNamePlaceholder: '可选',
    emailDesc: '邮箱（用于接收欢迎邮件和告警通知）',
    password: '密码',
    resetPassword: '重置密码（留空则不修改）',
    passwordPlaceholder: '至少 6 位',
    readOnlyUser: '只读用户',
    admin: '管理员',
    superAdmin: '超级管理员',
    usernameMin: '用户名至少 2 个字符',
    passwordMin: '密码至少 6 位',
    newPasswordMin: '新密码至少 6 位',
    confirmDelete: '确定要删除用户 "{name}" 吗？',
  },
  profile: {
    title: '个人设置',
    basicInfo: '基本信息',
    role: '角色',
    fullName: '姓名',
    fullNamePlaceholder: '请输入姓名',
    fullNameHint: '显示在顶部栏和邮件通知中',
    email: '邮箱',
    emailPlaceholder: '请输入邮箱地址',
    emailHint: '用于接收告警通知和密码重置邮件',
    saveChanges: '保存修改',
    changePassword: '修改密码',
    currentPassword: '当前密码',
    currentPasswordPlaceholder: '请输入当前密码',
    newPassword: '新密码',
    newPasswordPlaceholder: '请输入新密码（至少 6 位）',
    confirmPassword: '确认新密码',
    confirmPasswordPlaceholder: '请再次输入新密码',
    currentPasswordRequired: '请输入当前密码',
    newPasswordMin: '新密码长度不能少于 6 位',
    passwordMismatch: '两次输入的新密码不一致',
    profileUpdated: '个人信息已更新',
    saveFailed: '保存失败',
    passwordChanged: '密码修改成功',
    changeFailed: '修改失败',
    superAdmin: '超级管理员',
    admin: '管理员',
    readOnlyUser: '只读用户',
  },
  help: {
    searchPlaceholder: '搜索帮助内容...',
    noMatch: '没有找到匹配的内容',
    faq: '常见问题',
    contact: '联系我们',
    sections: {
      overview: `<h3>产品定位</h3>
      <p>SQL Server 监控平台是一套企业级数据库实时监控与告警系统，帮助 DBA 和运维人员全面掌握 SQL Server 实例的运行状态，快速发现并定位性能问题。</p>
      <h3>核心能力</h3>
      <ul>
        <li><strong>实时性能监控</strong>：CPU、内存、磁盘 I/O、连接数等核心指标秒级采集</li>
        <li><strong>死锁检测</strong>：自动捕获死锁事件，展示死锁图和涉及会话</li>
        <li><strong>慢查询分析</strong>：自动识别执行超时的 SQL 语句，提供优化建议</li>
        <li><strong>阻塞分析</strong>：实时展示阻塞链，快速定位阻塞源头</li>
        <li><strong>智能告警</strong>：多维度告警规则配置，支持多种通知方式</li>
        <li><strong>磁盘监控</strong>：数据文件和日志文件空间使用率追踪</li>
        <li><strong>索引分析</strong>：缺失索引和冗余索引识别，辅助索引优化</li>
        <li><strong>审计日志</strong>：完整记录用户操作和系统事件</li>
      </ul>
      <h3>支持环境</h3>
      <ul>
        <li>SQL Server 2012 / 2014 / 2016 / 2019 / 2022</li>
        <li>Windows 认证和 SQL Server 认证</li>
        <li>单实例和 Always On 可用性组</li>
      </ul>`,
      dashboard: `<h3>功能说明</h3>
      <p>总览页面是系统的默认首页，提供全局运行状态的一站式视图，帮助您快速了解所有监控实例的健康状况。</p>
      <h3>统计卡片</h3>
      <ul>
        <li><strong>实例总数</strong>：已配置的 SQL Server 实例数量</li>
        <li><strong>在线实例</strong>：当前连接正常、处于监控中的实例数</li>
        <li><strong>活动告警</strong>：未恢复的告警总数</li>
        <li><strong>严重告警</strong>：级别为"严重"的告警数量</li>
        <li><strong>慢查询数</strong>：今日捕获的慢查询总数</li>
        <li><strong>死锁次数</strong>：今日发生的死锁事件数</li>
        <li><strong>平均 CPU</strong>：所有在线实例的平均 CPU 使用率</li>
        <li><strong>平均磁盘</strong>：所有在线实例的平均磁盘使用率</li>
        <li><strong>活跃连接</strong>：所有实例的总连接数</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li>点击右上角"自定义"按钮，可选择显示/隐藏哪些统计卡片和图表</li>
        <li>点击时间范围下拉框，切换查看 1 小时 / 6 小时 / 24 小时 / 7 天的数据</li>
        <li>鼠标悬停在图表上，可查看具体时间点的数值</li>
        <li>点击图表右上角放大按钮，可全屏查看图表详情</li>
        <li>点击实例列表中的实例名称，可跳转到该实例的性能趋势页面</li>
      </ul>`,
      performance: `<h3>功能说明</h3>
      <p>性能趋势页面以折线图形式展示各项性能指标的历史变化曲线，帮助您分析性能走势、定位性能瓶颈。</p>
      <h3>监控指标</h3>
      <ul>
        <li><strong>CPU 使用率</strong>：SQL Server 进程占用的 CPU 百分比</li>
        <li><strong>内存使用率</strong>：SQL Server 占用内存占服务器总内存的比例</li>
        <li><strong>磁盘 I/O</strong>：数据文件读写速率（MB/s）</li>
        <li><strong>连接数</strong>：当前用户连接总数</li>
        <li><strong>批请求数</strong>：每秒批处理请求数（Batch Requests/sec）</li>
        <li><strong>等待时间</strong>：主要等待类型的累计等待时间</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li>顶部实例选择器：切换查看不同实例的性能数据</li>
        <li>时间范围切换：支持最近 1 小时 / 6 小时 / 24 小时 / 7 天 / 30 天</li>
        <li>点击图例中的指标名称，可单独显示/隐藏对应曲线</li>
        <li>双击图表可重置缩放状态</li>
        <li>鼠标悬停在曲线上，可查看精确的时间点和数值</li>
      </ul>
      <h3>正常参考值</h3>
      <ul>
        <li>CPU 使用率：持续超过 80% 需关注</li>
        <li>内存使用率：70%~90% 为正常区间（SQL Server 会尽可能使用内存）</li>
        <li>连接数：根据业务规模评估，突发增长可能意味着应用连接泄漏</li>
      </ul>`,
      deadlocks: `<h3>什么是死锁</h3>
      <p>死锁是指两个或多个事务在同一资源上相互占有并请求对方锁定的资源，从而造成永久阻塞的现象。SQL Server 会自动选择一个代价最小的事务作为"受害者"回滚，以打破死锁。</p>
      <h3>功能说明</h3>
      <p>死锁监控页面实时捕获并展示所有死锁事件，帮助您快速定位死锁原因和涉及的 SQL 语句。</p>
      <h3>查看详情</h3>
      <ul>
        <li>点击列表中的死锁记录，可展开查看详细信息</li>
        <li><strong>死锁时间</strong>：死锁发生的精确时间</li>
        <li><strong>受害者会话</strong>：被 SQL Server 选中回滚的会话 ID</li>
        <li><strong>涉及进程</strong>：参与死锁的所有会话信息</li>
        <li><strong>死锁 XML</strong>：原始的死锁图形描述（可复制到 SSMS 查看图形化死锁图）</li>
        <li><strong>涉及对象</strong>：死锁涉及的数据库对象（表、索引等）</li>
      </ul>
      <h3>常见死锁原因与解决思路</h3>
      <ul>
        <li><strong>访问顺序不一致</strong>：不同事务以不同顺序访问相同资源 → 统一访问顺序</li>
        <li><strong>事务过长</strong>：事务包含大量操作，持有锁时间过长 → 拆分事务，缩短执行时间</li>
        <li><strong>锁粒度太大</strong>：使用了较高的隔离级别或表锁 → 降低隔离级别，优化索引</li>
        <li><strong>缺少索引</strong>：查询扫描大量数据，持有过多行锁 → 添加合适的索引</li>
      </ul>`,
      alerts: `<h3>功能说明</h3>
      <p>告警管理页面集中展示所有触发的告警记录，支持按级别、时间、状态筛选，帮助您快速处理重要告警。</p>
      <h3>告警级别</h3>
      <ul>
        <li><span style="color:#ff4d4f"><strong>严重</strong></span>：影响业务正常运行，需立即处理（如数据库不可达、CPU 持续 100%）</li>
        <li><span style="color:#fa8c16"><strong>高</strong></span>：重要指标异常，需尽快关注（如磁盘使用率超过 90%）</li>
        <li><span style="color:#faad14"><strong>中</strong></span>：指标接近阈值，建议关注（如磁盘使用率超过 80%）</li>
        <li><span style="color:#52c41a"><strong>低</strong></span>：提示性信息，可择机处理</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li><strong>筛选</strong>：点击顶部筛选条件，按级别、时间范围、实例过滤告警</li>
        <li><strong>查看详情</strong>：点击告警记录，查看详细的指标数值、触发时间和阈值配置</li>
        <li><strong>跳转规则</strong>：点击告警规则名称，可跳转到对应告警规则的配置页</li>
      </ul>
      <h3>告警通知方式</h3>
      <p>告警触发时，系统会根据告警规则的配置，通过以下一种或多种方式通知：</p>
      <ul>
        <li>系统通知（站内消息，铃铛图标）</li>
        <li>邮件通知</li>
        <li>Webhook 推送（如企业微信、钉钉、飞书）</li>
        <li>浏览器桌面通知（需在浏览器中开启）</li>
      </ul>`,
      'slow-queries': `<h3>功能说明</h3>
      <p>慢查询分析自动捕获执行时间超过阈值的 SQL 语句，帮助您识别性能瓶颈，优化数据库查询效率。</p>
      <h3>阈值设置</h3>
      <p>默认慢查询阈值为 5 秒。管理员可在"系统设置"中调整慢查询捕获阈值。</p>
      <h3>操作说明</h3>
      <ul>
        <li><strong>筛选</strong>：按实例、数据库、时间范围筛选慢查询记录</li>
        <li><strong>排序</strong>：点击列表表头，可按执行时间、CPU 时间、逻辑读等维度排序</li>
        <li><strong>查看 SQL</strong>：点击记录可展开查看完整的 SQL 文本</li>
        <li><strong>执行计划</strong>：点击"查看执行计划"，可查看该查询的执行计划 XML</li>
      </ul>
      <h3>关键指标说明</h3>
      <ul>
        <li><strong>执行时间</strong>：语句总耗时（毫秒）</li>
        <li><strong>CPU 时间</strong>：消耗的 CPU 资源（毫秒）</li>
        <li><strong>逻辑读</strong>：从缓存中读取的页数（越少越好）</li>
        <li><strong>物理读</strong>：从磁盘读取的页数（应尽量减少）</li>
        <li><strong>执行次数</strong>：该语句被执行的次数</li>
      </ul>
      <h3>优化建议参考</h3>
      <ul>
        <li>检查是否缺少合适的索引（参考"索引分析"页面的缺失索引建议）</li>
        <li>避免在 WHERE 条件中对列使用函数，导致索引失效</li>
        <li>使用参数化查询，提高执行计划重用率</li>
        <li>大表分页查询使用 OFFSET/FETCH 或基于游标的方式</li>
      </ul>`,
      blocking: `<h3>什么是阻塞</h3>
      <p>阻塞是指一个事务持有资源的锁，而另一个事务需要等待该锁释放才能继续执行的现象。适度阻塞是正常的，但长时间阻塞会导致性能下降和应用超时。</p>
      <h3>功能说明</h3>
      <p>阻塞进程页面实时展示当前的阻塞链，以树状结构呈现阻塞者与被阻塞者的关系，帮助您快速定位阻塞源头。</p>
      <h3>查看阻塞链</h3>
      <ul>
        <li><strong>阻塞者（Blocker）</strong>：持有锁、导致其他会话等待的会话，位于阻塞链的顶端</li>
        <li><strong>被阻塞者（Blocked）</strong>：正在等待锁释放的会话</li>
        <li><strong>阻塞链</strong>：多级阻塞的关系（A 阻塞 B，B 又阻塞 C）</li>
        <li><strong>等待时间</strong>：会话已等待的时长，超过阈值标红显示</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li>点击阻塞会话左侧的箭头，展开查看完整阻塞链</li>
        <li>点击会话 ID，可查看该会话的详细信息（SQL 文本、登录名、主机名等）</li>
        <li><strong>KILL 会话</strong>：确认阻塞源头后，可终止该会话（需管理员权限）</li>
      </ul>
      <h3>预防阻塞的建议</h3>
      <ul>
        <li>保持事务尽可能简短，减少锁的持有时间</li>
        <li>确保查询使用合适的索引，避免全表扫描产生大量锁</li>
        <li>使用较低的事务隔离级别（如 READ COMMITTED SNAPSHOT）</li>
        <li>在应用层控制并发，避免热点资源争抢</li>
      </ul>`,
      disk: `<h3>功能说明</h3>
      <p>磁盘空间页面监控各实例的数据文件和日志文件空间使用情况，帮助您提前规划存储扩容，避免空间耗尽导致的数据库挂起。</p>
      <h3>监控内容</h3>
      <ul>
        <li><strong>数据文件</strong>：每个数据库的数据文件大小、已用空间、可用空间</li>
        <li><strong>日志文件</strong>：每个数据库的事务日志大小和使用率</li>
        <li><strong>磁盘卷</strong>：数据库文件所在磁盘卷的总空间和剩余空间</li>
        <li><strong>增长趋势</strong>：近 7 天 / 30 天的空间增长曲线</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li>顶部实例选择器切换不同实例</li>
        <li>点击数据库名称展开，查看该数据库的所有数据文件和日志文件详情</li>
        <li>空间使用率超过 80% 标黄，超过 90% 标红</li>
      </ul>
      <h3>常见空间问题与处理</h3>
      <ul>
        <li><strong>日志文件过大</strong>：检查是否为 FULL 恢复模式且未做日志备份 → 定期备份日志或切换为 SIMPLE 模式</li>
        <li><strong>数据文件增长快</strong>：分析哪些表占用空间最大 → 清理历史数据、重建索引释放空间</li>
        <li><strong>磁盘空间不足</strong>：扩容磁盘卷，或将部分数据库迁移到其他磁盘</li>
        <li><strong>tempdb 过大</strong>：检查是否有长时间运行的查询占用 tempdb → 优化查询或增加 tempdb 数据文件</li>
      </ul>`,
      indexes: `<h3>功能说明</h3>
      <p>索引分析页面通过分析 SQL Server 内部的索引使用统计和缺失索引 DMV，识别可能的性能优化点，帮助您合理设计索引。</p>
      <h3>缺失索引建议</h3>
      <p>SQL Server 会记录查询优化器认为"如果有这个索引，查询性能会更好"的场景。系统将这些建议汇总展示：</p>
      <ul>
        <li><strong>数据库</strong>：建议创建索引的数据库</li>
        <li><strong>表名</strong>：需要添加索引的表</li>
        <li><strong>相等列</strong>：建议作为索引键的等值查询列</li>
        <li><strong>不等列</strong>：建议作为索引键的范围查询列</li>
        <li><strong>包含列</strong>：建议作为 INCLUDE 的覆盖列</li>
        <li><strong>预期提升</strong>：用户开销百分比（越高说明潜在收益越大）</li>
      </ul>
      <h3>未使用索引</h3>
      <p>自 SQL Server 上次启动以来，从未被查询使用过的索引。这些索引只占用空间、拖慢写入速度，建议评估后删除：</p>
      <ul>
        <li>注意：主键和唯一约束即使未被查询使用，也不应随意删除（它们保证数据一致性）</li>
        <li>注意：索引使用统计自服务重启后累计，运行时间较短时参考价值有限</li>
      </ul>
      <h3>索引维护建议</h3>
      <ul>
        <li>碎片率 > 30%：建议重建索引（REBUILD）</li>
        <li>碎片率 5%~30%：建议重新组织索引（REORGANIZE）</li>
        <li>碎片率 < 5%：不需要维护</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>缺失索引建议仅供参考，创建索引前请评估对写入性能的影响</li>
        <li>不要盲目创建所有建议的索引，过多索引会降低 INSERT/UPDATE/DELETE 性能</li>
        <li>建议先在测试环境验证索引效果，再在生产环境实施</li>
      </ul>`,
      'alert-rules': `<h3>功能说明</h3>
      <p>告警规则页面用于创建和管理告警规则，定义"什么情况下触发告警"以及"如何通知"，是整个告警系统的核心配置。</p>
      <h3>规则组成</h3>
      <ul>
        <li><strong>规则名称</strong>：规则的标识名称，建议描述清晰（如"CPU使用率超过90%"）</li>
        <li><strong>指标分类</strong>：CPU、内存、磁盘、连接数、死锁、慢查询等</li>
        <li><strong>指标名</strong>：具体监控的指标项</li>
        <li><strong>条件</strong>：比较运算符（>、>=、<、<=、=）和阈值</li>
        <li><strong>持续时间</strong>：指标异常持续多长时间才触发告警（避免毛刺误报）</li>
        <li><strong>严重级别</strong>：严重 / 高 / 中 / 低</li>
        <li><strong>通知方式</strong>：系统通知 / 邮件 / Webhook</li>
        <li><strong>作用实例</strong>：应用到哪些实例（全部或指定实例）</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li><strong>新增规则</strong>：点击右上角"+ 新增规则"按钮</li>
        <li><strong>启用/禁用</strong>：点击开关，可临时禁用不需要的规则</li>
        <li><strong>编辑</strong>：点击操作列的编辑图标，修改规则配置</li>
        <li><strong>删除</strong>：删除不再需要的规则</li>
      </ul>
      <h3>内置规则</h3>
      <p>系统内置了一些常用的告警规则，安装后默认启用：</p>
      <ul>
        <li>实例连接失败（严重）</li>
        <li>CPU 使用率超过 90% 持续 5 分钟（高）</li>
        <li>磁盘使用率超过 90%（高）</li>
        <li>死锁发生（中）</li>
        <li>慢查询超过阈值（中）</li>
      </ul>`,
      instances: `<h3>功能说明</h3>
      <p>实例管理页面用于添加和管理需要监控的 SQL Server 实例，是系统运行的基础。</p>
      <h3>添加实例</h3>
      <p>点击"添加实例"按钮，填写以下信息：</p>
      <ul>
        <li><strong>实例名称</strong>：给实例起一个便于识别的名称（如"生产-订单库"）</li>
        <li><strong>主机地址</strong>：SQL Server 所在服务器的 IP 或主机名</li>
        <li><strong>端口</strong>：SQL Server 监听端口，默认 1433</li>
        <li><strong>实例名</strong>：默认实例留空，命名实例填实例名</li>
        <li><strong>认证方式</strong>：SQL Server 认证 或 Windows 认证</li>
        <li><strong>用户名/密码</strong>：用于连接的数据库账号</li>
        <li><strong>数据库</strong>：默认连接的数据库（可选）</li>
      </ul>
      <h3>账号权限要求</h3>
      <p>为了正常采集监控数据，连接账号需要以下权限：</p>
      <ul>
        <li>VIEW SERVER STATE 服务器级权限</li>
        <li>VIEW ANY DEFINITION 服务器级权限</li>
        <li>各数据库的 db_datareader 角色</li>
        <li>msdb 数据库的 SQLAgentReaderRole 角色（如需监控作业）</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li><strong>连接测试</strong>：添加或编辑实例时，先点击"测试连接"验证配置是否正确</li>
        <li><strong>启用/禁用</strong>：临时停止监控某个实例，但保留配置</li>
        <li><strong>状态说明</strong>：
          <ul>
            <li><span style="color:#52c41a">在线</span>：连接正常，正在监控</li>
            <li><span style="color:#ff4d4f">离线</span>：连接失败，无法采集数据</li>
            <li><span style="color:#bfbfbf">已禁用</span>：监控已手动关闭</li>
          </ul>
        </li>
      </ul>`,
      report: `<h3>功能说明</h3>
      <p>系统报告页面用于生成和导出数据库运行报告，帮助您定期回顾数据库健康状况，向上级汇报运维成果。</p>
      <h3>报告类型</h3>
      <ul>
        <li><strong>日报</strong>：过去 24 小时的运行概况</li>
        <li><strong>周报</strong>：过去 7 天的趋势和统计</li>
        <li><strong>月报</strong>：过去 30 天的全面分析</li>
        <li><strong>自定义</strong>：自由选择时间范围</li>
      </ul>
      <h3>报告内容</h3>
      <ul>
        <li>实例健康状态概览</li>
        <li>性能指标趋势图（CPU、内存、I/O、连接数）</li>
        <li>告警统计（按级别、按类型分布）</li>
        <li>Top 10 慢查询</li>
        <li>死锁事件汇总</li>
        <li>磁盘空间变化趋势</li>
        <li>索引优化建议</li>
      </ul>
      <h3>操作说明</h3>
      <ul>
        <li>选择实例和报告类型，点击"生成报告"</li>
        <li>报告生成后可在线预览</li>
        <li>点击"导出 PDF"可下载为 PDF 文件保存或打印</li>
        <li>点击"保存为图片"可将单个图表导出为 PNG</li>
      </ul>`,
      settings: `<h3>品牌设置</h3>
      <ul>
        <li><strong>系统名称</strong>：显示在登录页、侧边栏顶部的平台名称</li>
        <li><strong>Logo 图标</strong>：上传自定义 Logo 图片</li>
        <li><strong>主题色</strong>：自定义系统主题色（需支持，当前支持亮色/深色模式切换）</li>
      </ul>
      <h3>告警配置</h3>
      <ul>
        <li><strong>采集频率</strong>：性能指标采集间隔（默认 30 秒）</li>
        <li><strong>数据保留天数</strong>：监控数据保存时长（默认 30 天）</li>
        <li><strong>告警静默期</strong>：同一告警再次触发的最小间隔</li>
        <li><strong>慢查询阈值</strong>：慢查询捕获的执行时间阈值（默认 5 秒）</li>
      </ul>
      <h3>通知渠道</h3>
      <ul>
        <li><strong>邮件通知</strong>：配置 SMTP 服务器信息，支持告警邮件推送</li>
        <li><strong>Webhook</strong>：配置企业微信、钉钉、飞书等机器人 Webhook 地址</li>
        <li>配置后可点击"测试发送"验证配置是否正确</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>修改采集频率会影响数据精度和存储量，频率越高数据越精确但存储越大</li>
        <li>数据保留天数到期后数据会自动清理，重要报告请提前导出保存</li>
        <li>邮件和 Webhook 配置变更后，请务必进行测试验证</li>
      </ul>`,
      users: `<h3>功能说明</h3>
      <p>用户管理页面供管理员创建和管理系统账号，分配不同权限角色，确保系统安全使用。</p>
      <h3>角色说明</h3>
      <table style="width:100%;border-collapse:collapse;margin:12px 0;">
        <thead>
          <tr style="background:var(--bg-hover);">
            <th style="padding:8px 12px;border:1px solid var(--border-color);text-align:left;">角色</th>
            <th style="padding:8px 12px;border:1px solid var(--border-color);text-align:left;">权限范围</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>超级管理员</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">拥有所有权限，包括用户管理、系统设置、实例管理等</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>管理员</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">可配置告警规则、实例管理，但不能管理用户和修改系统核心设置</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:1px solid var(--border-color);"><strong>查看者</strong></td>
            <td style="padding:8px 12px;border:1px solid var(--border-color);">只读权限，可查看所有监控数据和告警，但不能做任何配置修改</td>
          </tr>
        </tbody>
      </table>
      <h3>操作说明</h3>
      <ul>
        <li><strong>新增用户</strong>：点击"新增用户"，填写用户名、姓名、邮箱、角色、初始密码</li>
        <li><strong>重置密码</strong>：点击操作列的钥匙图标，为用户重置密码</li>
        <li><strong>启用/禁用</strong>：禁用后用户无法登录系统</li>
        <li><strong>编辑</strong>：修改用户的姓名、邮箱、角色等信息</li>
      </ul>
      <h3>安全建议</h3>
      <ul>
        <li>遵循最小权限原则，只授予必要的角色</li>
        <li>定期审计用户列表，及时清理离职人员账号</li>
        <li>初始密码应设置为强密码，并要求用户首次登录后修改</li>
        <li>重要操作均记录在审计日志中，可在"审计日志"页面查看</li>
      </ul>`,
      faq: `<h3>Q：添加实例时连接失败怎么办？</h3>
      <p>A：请按以下步骤排查：</p>
      <ol>
        <li>确认主机地址和端口是否正确，网络是否通畅（ping 或 telnet 测试）</li>
        <li>确认 SQL Server 是否已启用 TCP/IP 协议（在 SQL Server 配置管理器中查看）</li>
        <li>确认防火墙是否放行了 SQL Server 端口（默认 1433）</li>
        <li>确认账号密码正确，且账号有足够权限（VIEW SERVER STATE 等）</li>
        <li>如果是命名实例，确认 SQL Server Browser 服务已启动</li>
      </ol>
      <h3>Q：为什么告警触发了但没有收到通知？</h3>
      <p>A：请检查以下几点：</p>
      <ol>
        <li>确认告警规则中的通知方式已勾选</li>
        <li>如果是邮件通知，检查"系统设置 → 通知渠道"中的 SMTP 配置是否正确</li>
        <li>如果是 Webhook，检查 Webhook 地址是否有效，机器人是否在群内</li>
        <li>检查是否处于告警静默期内，短时间内重复告警可能被抑制</li>
        <li>查看通知是否进入了垃圾邮件或被拦截</li>
      </ol>
      <h3>Q：监控数据不更新怎么办？</h3>
      <p>A：可能原因和解决方案：</p>
      <ol>
        <li>检查实例状态是否为"在线"，如果离线则无法采集</li>
        <li>检查后端服务是否正常运行</li>
        <li>尝试手动刷新页面，排除浏览器缓存问题</li>
        <li>查看后端日志是否有报错信息</li>
      </ol>
      <h3>Q：忘记登录密码怎么办？</h3>
      <p>A：</p>
      <ul>
        <li>如果系统配置了邮件服务，可在登录页点击"忘记密码"，通过邮箱重置</li>
        <li>如果是管理员账号且无法通过邮件重置，可联系超级管理员在用户管理中重置密码</li>
        <li>如果唯一的超级管理员也忘记了，需要通过数据库直接修改或重新初始化</li>
      </ul>
      <h3>Q：如何开启深色模式？</h3>
      <p>A：点击页面右上角的月亮/太阳图标，即可在亮色和深色模式之间切换。系统会记住您的选择。</p>
      <h3>Q：如何升级系统到新版本？</h3>
      <p>A：当系统检测到新版本时，侧边栏底部和顶部栏的版本号旁会出现黄色提示点，点击后可查看更新说明。升级步骤：</p>
      <ol>
        <li>备份数据库和配置文件</li>
        <li>拉取最新代码（git pull）</li>
        <li>重新构建 Docker 镜像并启动</li>
      </ol>
      <h3>Q：支持监控多少个实例？</h3>
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>`,
      contact: `<h3>技术支持</h3>
      <p>如果在使用过程中遇到问题，可以通过以下方式联系我们：</p>
      <ul>
        <li><strong>部门</strong>：太阳谷信息技术部</li>
        <li><strong>邮箱</strong>：请联系 IT 支持邮箱</li>
        <li><strong>企业微信</strong>：搜索 IT 支持群</li>
      </ul>
      <h3>反馈建议</h3>
      <p>我们非常重视您的反馈，如果您有功能建议、使用体验或发现 Bug，欢迎随时反馈：</p>
      <ul>
        <li>描述清楚遇到的问题或建议的功能</li>
        <li>如果是 Bug，请附上截图和操作步骤</li>
        <li>提供使用的浏览器、系统版本等环境信息</li>
      </ul>
      <h3>版本信息</h3>
      <p>当前版本号请查看侧边栏底部或顶部栏。点击版本号可查看是否有新版本可用。</p>`,
    },
  },
  login: {
    slogan: '实时监控 · 智能告警 · 深度分析',
    feature1: '全方位性能指标监控',
    feature2: '智能告警与多渠道通知',
    feature3: 'AI 驱动的分析报告',
    copyright: '太阳谷信息技术部',
    welcome: '欢迎登录',
    subtitle: '请使用您的账号登录系统',
    username: '用户名',
    usernamePlaceholder: '请输入用户名',
    password: '密码',
    passwordPlaceholder: '请输入密码',
    forgotPassword: '忘记密码？',
    loginButton: '登 录',
    logging: '登录中...',
    loginFailed: '登录失败，请稍后再试',
  },
  forgotPassword: {
    title: '找回密码',
    subtitle: '请输入您的注册邮箱，我们将发送验证码',
    email: '邮箱地址',
    emailPlaceholder: '请输入注册邮箱',
    sending: '发送中...',
    sendCode: '发送验证码',
    rememberPassword: '想起密码了？',
    backToLogin: '返回登录',
    resetTitle: '重置密码',
    codeSentTo: '验证码已发送至',
    code: '验证码',
    codePlaceholder: '请输入 6 位验证码',
    resend: '重发',
    newPassword: '新密码',
    newPasswordPlaceholder: '请输入新密码（至少 6 位）',
    confirmPassword: '确认新密码',
    confirmPasswordPlaceholder: '请再次输入新密码',
    resetting: '重置中...',
    confirmReset: '确认重置',
    backToPrev: '返回上一步',
    resetSuccess: '密码重置成功',
    resetSuccessDesc1: '您的密码已成功重置。',
    resetSuccessDesc2: '请使用新密码重新登录系统。',
    loginNow: '立即登录',
    sendFailed: '发送失败，请稍后再试',
    codeRequired: '请输入 6 位数字验证码',
    passwordMin: '密码长度不能少于 6 位',
    passwordMismatch: '两次输入的密码不一致',
    resetFailed: '重置失败，请稍后再试',
  },
  setup: {
    platformTitle: 'SQL 监控平台',
    platformDesc: '数据库查询性能监控与分析系统',
    welcomeTitle: '欢迎使用 SQL 监控平台',
    welcomeDesc1: '本系统可以帮助您实时监控 SQL Server 数据库的性能指标、',
    welcomeDesc2: '检测死锁事件、分析慢查询、管理告警通知，',
    welcomeDesc3: '并提供 AI 驱动的智能分析与报告生成。',
    feature1: '全方位性能指标实时监控',
    feature2: '智能告警与多渠道通知（邮件、企业微信）',
    feature3: 'AI 驱动的死锁分析与系统报告',
    feature4: '支持多 SQL Server 实例集中管理',
    startInstall: '开始安装',
    createAdmin: '创建超级管理员',
    createAdminDesc: '设置系统超级管理员账号，用于首次登录和管理系统',
    username: '用户名',
    usernamePlaceholder: '请输入管理员用户名',
    displayName: '显示名称',
    displayNamePlaceholder: '请输入管理员显示名称（可选）',
    password: '密码',
    passwordPlaceholder: '请输入密码',
    confirmPassword: '确认密码',
    confirmPasswordPlaceholder: '请再次输入密码',
    prevStep: '上一步',
    creating: '创建中...',
    createAndContinue: '创建并继续',
    basicConfig: '基础系统配置',
    basicConfigDesc: '配置系统时区和数据保留策略',
    timezone: '系统时区',
    timezoneDesc: '系统时区用于日志和报表时间显示',
    beijing: '北京时间',
    tokyo: '东京时间',
    newyork: '纽约时间',
    losangeles: '洛杉矶时间',
    london: '伦敦时间',
    dataRetention: '数据保留天数',
    dataRetentionDesc: '超过此天数的监控数据将被自动清理，建议 90-365 天',
    saving: '保存中...',
    saveAndFinish: '保存并完成',
    installComplete: '安装完成！',
    completeDesc1: '系统已成功完成初始化配置。',
    completeDesc2: '您现在可以使用刚才创建的超级管理员账号登录系统。',
    adminAccount: '管理员账号',
    adminTimeZone: '系统时区',
    dataRetentionLabel: '数据保留',
    loginNow: '立即登录',
    steps: {
      welcome: '欢迎',
      intro: '系统介绍',
      admin: '管理员',
      createAccount: '创建账号',
      config: '配置',
      systemSettings: '系统设置',
      complete: '完成',
      installComplete: '安装完成',
    },
    usernameRequired: '请输入用户名',
    usernameMin: '用户名至少 2 个字符',
    passwordRequired: '请输入密码',
    passwordMin: '密码至少 6 个字符',
    confirmRequired: '请确认密码',
    passwordMismatch: '两次密码不一致',
    createAdminFailed: '创建管理员失败',
    saveConfigFailed: '保存配置失败',
  },
  aiAssistant: {
    title: 'AI 助手',
    subtitle: '让 AI 自动规划并执行任务',
    newTask: '+ 新建任务',
    inputPlaceholder: '描述您想要执行的任务，例如：分析数据库健康状况...',
    sending: '正在分析...',
    planGenerated: '已生成执行计划，共 {count} 个步骤',
    taskCompleted: '任务已完成',
    taskRunning: '执行中...',
    taskFailed: '任务失败',
    taskPending: '等待执行',
    stepRunning: '执行中...',
    stepCompleted: '已完成',
    stepFailed: '失败',
    stepPending: '等待中',
    noTasks: '暂无任务',
    noTasksHint: '点击上方按钮创建新任务',
    deleteTask: '删除任务',
    confirmDelete: '确定要删除该任务吗？',
    noResult: '暂无分析结果',
    fetchFailed: '获取任务列表失败',
    createFailed: '创建任务失败',
    deleteFailed: '删除任务失败',
    followUpPlaceholder: '基于以上分析继续提问...',
    followUpFailed: '追问失败',
    userMessage: '用户',
    aiResponse: 'AI 助手',
    stepResult: '步骤结果',
    followUp: '追问',
    taskPlanning: '思考 / 任务拆解',
    diagnosticReport: '诊断报告',
    generatingReport: '正在生成报告...',
    taskAwaitingReport: '等待报告生成',
  },
}
