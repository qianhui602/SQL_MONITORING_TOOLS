<template>
  <div class="help-page">
    <div class="help-search">
      <div class="search-box">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchText" type="text" placeholder="搜索帮助内容..." class="search-input" />
      </div>
    </div>
    <div class="help-layout">
      <nav class="help-nav">
        <div v-for="section in filteredSections" :key="section.id" class="nav-item" :class="{ active: activeSection === section.id }" @click="scrollTo(section.id)">{{ section.title }}</div>
      </nav>
      <div class="help-content" ref="contentRef">
        <div v-for="section in filteredSections" :key="section.id" :id="section.id" class="help-section">
          <h2 class="section-title">{{ section.title }}</h2>
          <div v-html="section.content" class="section-body"></div>
        </div>
        <div v-if="filteredSections.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <p>没有找到匹配的内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const searchText = ref('')
const activeSection = ref('overview')
const contentRef = ref(null)

const sections = [
  {
    id: 'overview',
    title: '系统概述',
    content: `
      <h3>产品定位</h3>
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
      </ul>
    `
  },
  {
    id: 'dashboard',
    title: '总览仪表盘',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'performance',
    title: '性能趋势',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'deadlocks',
    title: '死锁监控',
    content: `
      <h3>什么是死锁</h3>
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
      </ul>
    `
  },
  {
    id: 'alerts',
    title: '告警管理',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'slow-queries',
    title: '慢查询分析',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'blocking',
    title: '阻塞进程',
    content: `
      <h3>什么是阻塞</h3>
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
      </ul>
    `
  },
  {
    id: 'disk',
    title: '磁盘空间',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'indexes',
    title: '索引分析',
    content: `
      <h3>功能说明</h3>
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
        <li>碎片率 &gt; 30%：建议重建索引（REBUILD）</li>
        <li>碎片率 5%~30%：建议重新组织索引（REORGANIZE）</li>
        <li>碎片率 &lt; 5%：不需要维护</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>缺失索引建议仅供参考，创建索引前请评估对写入性能的影响</li>
        <li>不要盲目创建所有建议的索引，过多索引会降低 INSERT/UPDATE/DELETE 性能</li>
        <li>建议先在测试环境验证索引效果，再在生产环境实施</li>
      </ul>
    `
  },
  {
    id: 'alert-rules',
    title: '告警规则',
    content: `
      <h3>功能说明</h3>
      <p>告警规则页面用于创建和管理告警规则，定义"什么情况下触发告警"以及"如何通知"，是整个告警系统的核心配置。</p>
      <h3>规则组成</h3>
      <ul>
        <li><strong>规则名称</strong>：规则的标识名称，建议描述清晰（如"CPU使用率超过90%"）</li>
        <li><strong>指标分类</strong>：CPU、内存、磁盘、连接数、死锁、慢查询等</li>
        <li><strong>指标名</strong>：具体监控的指标项</li>
        <li><strong>条件</strong>：比较运算符（&gt;、&gt;=、&lt;、&lt;=、=）和阈值</li>
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
      </ul>
    `
  },
  {
    id: 'instances',
    title: '实例管理',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'report',
    title: '系统报告',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'settings',
    title: '系统设置',
    content: `
      <h3>功能说明</h3>
      <p>系统设置页面供管理员配置系统参数，包括品牌定制、告警配置、通知渠道、数据采集等。</p>
      <h3>品牌设置</h3>
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
      </ul>
    `
  },
  {
    id: 'users',
    title: '用户管理',
    content: `
      <h3>功能说明</h3>
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
      </ul>
    `
  },
  {
    id: 'faq',
    title: '常见问题',
    content: `
      <h3>Q：添加实例时连接失败怎么办？</h3>
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
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>
    `
  },
  {
    id: 'contact',
    title: '联系我们',
    content: `
      <h3>技术支持</h3>
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
      <p>当前版本号请查看侧边栏底部或顶部栏。点击版本号可查看是否有新版本可用。</p>
    `
  }
]

const filteredSections = computed(() => {
  if (!searchText.value.trim()) return sections
  const kw = searchText.value.trim().toLowerCase()
  return sections.filter(s => s.title.toLowerCase().includes(kw) || s.content.toLowerCase().includes(kw))
})

function scrollTo(id) {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

let observer = null

onMounted(() => {
  nextTick(() => {
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) { if (entry.isIntersecting) activeSection.value = entry.target.id }
    }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 })
    const container = contentRef.value
    if (container) container.querySelectorAll('.help-section').forEach(el => observer.observe(el))
  })
})

onBeforeUnmount(() => { if (observer) observer.disconnect() })
</script>

<style scoped>
.help-page { display: flex; flex-direction: column; gap: 16px; height: calc(100vh - 140px); }
.help-search { flex-shrink: 0; }
.search-box { display: flex; align-items: center; gap: 8px; background: var(--bg-card); border-radius: 8px; padding: 10px 16px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); }
.search-icon { color: #999; flex-shrink: 0; }
.search-input { flex: 1; border: none; outline: none; font-size: 14px; background: transparent; color: var(--text-primary); }
.search-input::placeholder { color: #bbb; }
.help-layout { display: flex; gap: 16px; flex: 1; min-height: 0; }
.help-nav { width: 180px; flex-shrink: 0; background: var(--bg-card); border-radius: 8px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); padding: 8px; overflow-y: auto; align-self: flex-start; position: sticky; top: 0; }
.nav-item { padding: 8px 12px; border-radius: 6px; font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.active { background: #1890ff; color: #fff; }
.help-content { flex: 1; overflow-y: auto; padding-right: 8px; }
.help-section { background: var(--bg-card); border-radius: 8px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); padding: 24px 28px; margin-bottom: 12px; scroll-margin-top: 8px; }
.section-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px 0; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.section-body { font-size: 14px; line-height: 1.8; color: var(--text-secondary); }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; color: #bbb; gap: 12px; }
.empty-state p { font-size: 14px; }
@media (max-width: 768px) {
  .help-layout { flex-direction: column; }
  .help-nav { width: 100%; position: static; display: flex; flex-wrap: wrap; gap: 4px; padding: 8px; }
  .nav-item { padding: 6px 10px; font-size: 12px; }
}
</style>