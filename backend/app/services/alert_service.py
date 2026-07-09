"""
告警规则引擎

定义告警规则数据结构和规则检查引擎，
支持自定义告警规则、冷却期控制和多渠道通知。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from sqlalchemy import and_, select

from app.config import settings
from app.models.alert import AlertLog
from app.models.alert_rule import AlertRule as AlertRuleModel
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """告警规则定义

    Attributes:
        alert_type: 告警类型标识（如 memory_high / deadlock_detected）
        severity: 严重级别（low / medium / high / critical）
        condition_func: 条件判断函数，接收 metrics_data 返回 bool
        message_template: 消息模板，支持 format 占位符
        cooldown_minutes: 冷却时间（分钟），相同类型告警在该时间内不重复触发
    """

    alert_type: str
    severity: str
    condition_func: Callable[[Dict[str, Any]], bool]
    message_template: str
    cooldown_minutes: int = 10


class AlertEngine:
    """告警规则引擎

    接收采集的指标数据，检查预定义的告警规则，
    在规则触发时创建告警记录并通过通知渠道发送。
    """

    # ---------- 内置告警规则 ----------

    @staticmethod
    def _condition_memory_high(metrics_data: Dict[str, Any]) -> bool:
        """判断内存使用率是否 > 85%

        从 metrics_data 中提取 os_memory 分类下的 memory_usage_pct 指标。
        实际持续时长的判断在 check_rules 中通过 DB 历史数据验证。

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            bool: 当前内存使用率 > 85% 返回 True
        """
        for metric in metrics_data.get("metrics", []):
            if metric.get("category") == "os_memory":
                pct = metric.get("values", {}).get("memory_usage_pct")
                if pct is not None and float(pct) > 85:
                    return True
        return False

    @staticmethod
    def _condition_deadlock(metrics_data: Dict[str, Any]) -> bool:
        """判断是否检测到死锁

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            bool: 存在死锁事件返回 True
        """
        return bool(metrics_data.get("deadlocks"))

    @staticmethod
    def _condition_collection_interrupted(metrics_data: Dict[str, Any]) -> bool:
        """判断采集任务是否中断

        当前采集周期未获取到任何指标和死锁数据时判定为中断。

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            bool: 当前周期无数据返回 True
        """
        has_metrics = bool(metrics_data.get("metrics"))
        has_deadlocks = bool(metrics_data.get("deadlocks"))
        return not has_metrics and not has_deadlocks

    @staticmethod
    def _condition_connection_lost(metrics_data: Dict[str, Any]) -> bool:
        """判断是否有实例连接断开

        Args:
            metrics_data: 采集的完整指标数据（含 connection_status）

        Returns:
            bool: 存在连接断开的实例返回 True
        """
        for conn_status in metrics_data.get("connection_status", []):
            if not conn_status.get("is_connected", True):
                return True
        return False

    @staticmethod
    def _condition_connection_recovered(metrics_data: Dict[str, Any]) -> bool:
        """判断是否有实例连接恢复（前次断开，本次连接成功）

        Args:
            metrics_data: 采集的完整指标数据（含 connection_status）

        Returns:
            bool: 存在连接恢复的实例返回 True
        """
        for conn_status in metrics_data.get("connection_status", []):
            if conn_status.get("is_connected", True) and conn_status.get("previous_was_disconnected", False):
                return True
        return False

    def __init__(self, db_session_factory) -> None:
        """初始化告警引擎

        Args:
            db_session_factory: 异步数据库 session 工厂（async_sessionmaker）
        """
        self.session_factory = db_session_factory
        self.notification_service = NotificationService()

        # 跟踪每个实例的前次连接状态（server_address -> was_disconnected）
        self._last_connection_state: Dict[str, bool] = {}

        # 内置 5 条告警规则
        self._builtin_rules: List[AlertRule] = [
            AlertRule(
                alert_type="memory_high",
                severity="critical",
                condition_func=self._condition_memory_high,
                message_template=(
                    "## 内存使用率持续偏高\n\n"
                    "- **当前内存使用率**: {memory_pct:.1f}%\n"
                    "- **触发阈值**: > 85%\n"
                    "- **持续时长**: 已超过 5 分钟\n\n"
                    "请检查 SQL Server 内存配置或考虑扩容。"
                ),
                cooldown_minutes=10,
            ),
            AlertRule(
                alert_type="deadlock_detected",
                severity="high",
                condition_func=self._condition_deadlock,
                message_template=(
                    "## 检测到死锁事件\n\n"
                    "- **受害者会话 ID**: {victim_session_id}\n"
                    "- **涉及对象**: {involved_objects}\n"
                    "- **发生时间**: {occur_at}\n\n"
                    "请检查相关 SQL 语句并优化事务逻辑。"
                ),
                cooldown_minutes=5,
            ),
            AlertRule(
                alert_type="collection_interrupted",
                severity="high",
                condition_func=self._condition_collection_interrupted,
                message_template=(
                    "## 采集任务异常中断\n\n"
                    "- **连续 3 次采集周期**未获取到新数据\n"
                    "- **最后记录时间**: {last_record_time}\n"
                    "- **当前时间**: {current_time}\n\n"
                    "请检查 SQL Server 连接状态或网络连通性。"
                ),
                cooldown_minutes=15,
            ),
            AlertRule(
                alert_type="connection_lost",
                severity="critical",
                condition_func=self._condition_connection_lost,
                message_template=(
                    "## SQL Server 连接断开\n\n"
                    "- **实例**: {server_address}\n"
                    "- **错误信息**: {error_message}\n"
                    "- **最后连接时间**: {last_connected_at}\n"
                    "- **触发时间**: {current_time}\n\n"
                    "请立即检查 SQL Server 服务状态和网络连通性。"
                ),
                cooldown_minutes=10,
            ),
            AlertRule(
                alert_type="connection_recovered",
                severity="low",
                condition_func=self._condition_connection_recovered,
                message_template=(
                    "## SQL Server 连接已恢复\n\n"
                    "- **实例**: {server_address}\n"
                    "- **断开时长**: {down_duration}\n"
                    "- **恢复时间**: {current_time}\n\n"
                    "连接已恢复正常。"
                ),
                cooldown_minutes=5,
            ),
        ]

    async def check_rules(
        self, metrics_data: Dict[str, Any]
    ) -> List[Tuple[str, str, str]]:
        """检查所有告警规则

        对每条规则依次执行条件判断，并通过数据库查询进行辅助验证
        （如内存持续偏高和持续中断检测）。

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            list: 触发的告警信息列表，每个元素为
                  (alert_type, severity, message) 元组
        """
        triggered: List[Tuple[str, str, str]] = []

        for rule in self._builtin_rules:
            if not rule.condition_func(metrics_data):
                continue

            # ------ 规则 1: 内存使用率持续 > 85%（需验证持续 5 分钟） ------
            if rule.alert_type == "memory_high":
                memory_pct = self._extract_memory_pct(metrics_data)
                if memory_pct is None:
                    continue

                # 查询 DB 中最近 5 分钟的内存使用率记录
                if not await self._is_memory_high_sustained(duration_minutes=5):
                    logger.debug(
                        "Memory high detected but not sustained for 5 minutes, skipping alert"
                    )
                    continue

                message = rule.message_template.format(memory_pct=memory_pct)

            # ------ 规则 2: 死锁检测 ------
            elif rule.alert_type == "deadlock_detected":
                deadlocks = metrics_data.get("deadlocks", [])
                if not deadlocks:
                    continue
                dl = deadlocks[0]
                message = rule.message_template.format(
                    victim_session_id=dl.get("victim_session_id", "N/A"),
                    involved_objects=", ".join(
                        str(o) for o in dl.get("involved_objects", [])
                    ) or "N/A",
                    occur_at=dl.get("occur_at", "N/A"),
                )

            # ------ 规则 3: 采集任务中断（验证连续 3 次无新数据） ------
            elif rule.alert_type == "collection_interrupted":
                if not await self._is_collection_truly_interrupted():
                    logger.debug(
                        "Empty collection detected but not 3 consecutive, skipping alert"
                    )
                    continue

                last_time = await self._get_last_collection_time()
                message = rule.message_template.format(
                    last_record_time=last_time or "无记录",
                    current_time=datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S UTC"
                    ),
                )

            # ------ 规则 4: 连接断开 ------
            elif rule.alert_type == "connection_lost":
                lost_instances = [
                    s for s in metrics_data.get("connection_status", [])
                    if not s.get("is_connected", True)
                ]
                if not lost_instances:
                    continue

                # 只报告第一个断开的实例
                inst = lost_instances[0]
                message = rule.message_template.format(
                    server_address=inst.get("server_address", "未知"),
                    error_message=inst.get("connection_error", "无详细信息"),
                    last_connected_at=inst.get("last_connected_at", "未知"),
                    current_time=datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S UTC"
                    ),
                )

            # ------ 规则 5: 连接恢复 ------
            elif rule.alert_type == "connection_recovered":
                recovered_instances = [
                    s for s in metrics_data.get("connection_status", [])
                    if s.get("is_connected", True) and s.get("previous_was_disconnected", False)
                ]
                if not recovered_instances:
                    continue

                inst = recovered_instances[0]
                message = rule.message_template.format(
                    server_address=inst.get("server_address", "未知"),
                    down_duration=inst.get("down_duration", "未知"),
                    current_time=datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S UTC"
                    ),
                )

            else:
                # 未知规则类型，不应到达这里
                continue

            triggered.append((rule.alert_type, rule.severity, message))

        return triggered

    # ========== 辅助方法 ==========

    def _extract_memory_pct(self, metrics_data: Dict[str, Any]) -> Optional[float]:
        """从 metrics_data 中提取内存使用率

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            float or None: 内存使用率百分比
        """
        for metric in metrics_data.get("metrics", []):
            if metric.get("category") == "os_memory":
                pct = metric.get("values", {}).get("memory_usage_pct")
                if pct is not None:
                    return float(pct)
        return None

    async def _is_memory_high_sustained(self, duration_minutes: int = 5) -> bool:
        """查询数据库，验证内存使用率是否持续高于 85%

        Args:
            duration_minutes: 持续时长（分钟）

        Returns:
            bool: 持续偏高返回 True
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=duration_minutes)

        async with self.session_factory() as session:
            try:
                from sqlalchemy import text

                query = text("""
                    SELECT COUNT(*) as total,
                           COUNT(*) FILTER (WHERE metric_value > 85) as high_count
                    FROM metrics
                    WHERE category = 'os_memory'
                      AND metric_name = 'memory_usage_pct'
                      AND collected_at >= :since
                """)
                # 查出间隔数（约 5 分钟 / 60s = 5 条）
                result = await session.execute(query, {"since": since})
                row = result.fetchone()

                if row is None or row.total == 0:
                    return False

                # 如果 80% 以上的记录都 > 85%，认为持续偏高
                threshold_ratio = 0.8
                return (row.high_count / row.total) >= threshold_ratio

            except Exception as e:
                logger.error("Failed to check sustained memory high: %s", e)
                return False

    async def _is_collection_truly_interrupted(self) -> bool:
        """验证采集是否真正中断

        检查 metrics 表中最新的 collected_at 是否早于 3 个采集周期之前。

        Returns:
            bool: 确认中断返回 True
        """
        interval = settings.SCHEDULER_INTERVAL_SECONDS
        threshold = timedelta(seconds=interval * 3)

        async with self.session_factory() as session:
            try:
                from sqlalchemy import text

                query = text("""
                    SELECT MAX(collected_at) as last_collected
                    FROM metrics
                """)
                result = await session.execute(query)
                row = result.fetchone()

                if row is None or row.last_collected is None:
                    # 从未采集过数据，但当前也没有数据 → 中断
                    return True

                last_time = row.last_collected
                if isinstance(last_time, str):
                    from dateutil import parser

                    last_time = parser.parse(last_time)

                # 确保 last_time 有时区信息
                now = datetime.now(timezone.utc)
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)

                return (now - last_time) >= threshold

            except Exception as e:
                logger.error("Failed to check collection interruption: %s", e)
                return False

    async def _get_last_collection_time(self) -> Optional[str]:
        """获取最后一次成功采集的时间

        Returns:
            str or None: ISO 格式时间字符串
        """
        async with self.session_factory() as session:
            try:
                from sqlalchemy import text

                query = text("""
                    SELECT MAX(collected_at) as last_collected
                    FROM metrics
                """)
                result = await session.execute(query)
                row = result.fetchone()
                if row and row.last_collected:
                    return str(row.last_collected)
                return None
            except Exception as e:
                logger.error("Failed to get last collection time: %s", e)
                return None

    async def _is_in_cooldown(self, alert_type: str, cooldown_minutes: int) -> bool:
        """检查指定类型的告警是否处于冷却期

        在冷却期内，相同类型的告警不重复触发。

        Args:
            alert_type: 告警类型
            cooldown_minutes: 冷却时长（分钟）

        Returns:
            bool: 处于冷却期返回 True
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)

        async with self.session_factory() as session:
            try:
                stmt = select(AlertLog).where(
                    and_(
                        AlertLog.alert_type == alert_type,
                        AlertLog.triggered_at >= since,
                    )
                ).limit(1)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                return existing is not None
            except Exception as e:
                logger.error(
                    "Failed to check cooldown for %s: %s", alert_type, e
                )
                # 查询失败时保守处理：跳过告警
                return True

    async def create_alert(
        self, alert_type: str, severity: str, message: str
    ) -> Optional[AlertLog]:
        """创建告警记录并发送通知

        将告警写入 PostgreSQL，然后调用通知服务。

        Args:
            alert_type: 告警类型
            severity: 严重级别
            message: 告警消息

        Returns:
            AlertLog or None: 成功返回 AlertLog 对象，失败返回 None
        """
        alert = AlertLog(
            alert_type=alert_type,
            severity=severity,
            message=message,
            triggered_at=datetime.now(timezone.utc),
            acknowledged=False,
            notification_sent=False,
        )

        async with self.session_factory() as session:
            try:
                session.add(alert)
                await session.commit()
                await session.refresh(alert)
                logger.info(
                    "Alert created: id=%s type=%s severity=%s",
                    alert.id,
                    alert.alert_type,
                    alert.severity,
                )
            except Exception as e:
                await session.rollback()
                logger.error("Failed to save alert to database: %s", e)
                return None

        # 发送通知
        try:
            subject = f"[{severity.upper()}] SQL Monitor Alert - {alert_type}"
            notify_result = await self.notification_service.notify_all(
                subject=subject, body=message
            )

            # 更新通知发送状态
            async with self.session_factory() as session:
                try:
                    alert.notification_sent = any(notify_result.values())
                    await session.merge(alert)
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    logger.warning(
                        "Failed to update notification_sent flag: %s", e
                    )

            logger.info(
                "Notification sent for alert %s: %s", alert.id, notify_result
            )

        except Exception as e:
            logger.error(
                "Failed to send notification for alert %s: %s",
                alert.id,
                e,
            )

        return alert

    async def process_metrics(
        self, metrics_data: Dict[str, Any]
    ) -> List[AlertLog]:
        """执行完整告警流程

        1. 检查所有内置告警规则
        2. 加载并检查数据库中的自定义告警规则
        3. 对触发的规则检查冷却期
        4. 创建告警记录并发送通知

        Args:
            metrics_data: 采集的完整指标数据
                          (格式: {"metrics": [...], "deadlocks": [...]})

        Returns:
            list: 新创建的 AlertLog 对象列表（可能为空）
        """
        created_alerts: List[AlertLog] = []

        # 步骤1: 检查内置规则
        triggered = await self.check_rules(metrics_data)

        # 步骤2: 加载并检查数据库中的自定义规则
        custom_triggered = await self._check_custom_rules(metrics_data)
        triggered.extend(custom_triggered)

        if not triggered:
            logger.debug("No alert rules triggered")
            return created_alerts

        logger.info(
            "%d alert rule(s) triggered: %s",
            len(triggered),
            [t[0] for t in triggered],
        )

        # 步骤3 & 4: 检查冷却期 → 创建告警
        for alert_type, severity, message in triggered:
            # 查找对应规则的冷却时间
            cooldown = self._get_cooldown_minutes(alert_type)

            if await self._is_in_cooldown(alert_type, cooldown):
                logger.info(
                    "Alert type '%s' is in cooldown period (%d min), skipping",
                    alert_type,
                    cooldown,
                )
                continue

            alert = await self.create_alert(alert_type, severity, message)
            if alert is not None:
                created_alerts.append(alert)

        return created_alerts

    async def _load_custom_rules(self) -> List[AlertRuleModel]:
        """从数据库加载所有启用的自定义告警规则

        过滤掉处于静默时段的规则。

        Returns:
            list: 启用的自定义告警规则列表
        """
        async with self.session_factory() as session:
            try:
                stmt = select(AlertRuleModel).where(
                    AlertRuleModel.enabled == True
                )
                result = await session.execute(stmt)
                rules = result.scalars().all()

                # 过滤掉处于静默时段的规则
                now_time = datetime.now(timezone.utc).time()
                active_rules = []
                for rule in rules:
                    if rule.silence_start is not None and rule.silence_end is not None:
                        if rule.silence_start <= rule.silence_end:
                            # 正常时段：start < end
                            if rule.silence_start <= now_time <= rule.silence_end:
                                logger.debug(
                                    "Custom rule '%s' is in silence period, skipping",
                                    rule.name,
                                )
                                continue
                        else:
                            # 跨天时段：如 22:00 - 06:00
                            if now_time >= rule.silence_start or now_time <= rule.silence_end:
                                logger.debug(
                                    "Custom rule '%s' is in overnight silence period, skipping",
                                    rule.name,
                                )
                                continue
                    active_rules.append(rule)

                logger.debug("Loaded %d active custom alert rules", len(active_rules))
                return active_rules
            except Exception as e:
                logger.error("Failed to load custom alert rules: %s", e)
                return []

    async def _check_custom_rules(
        self, metrics_data: Dict[str, Any]
    ) -> List[Tuple[str, str, str]]:
        """检查数据库中的自定义告警规则

        Args:
            metrics_data: 采集的完整指标数据

        Returns:
            list: 触发的告警信息列表
        """
        triggered: List[Tuple[str, str, str]] = []
        custom_rules = await self._load_custom_rules()

        if not custom_rules:
            return triggered

        # 构建指标查找表：{(category, metric_name): value}
        metric_lookup: Dict[Tuple[str, str], float] = {}
        for metric in metrics_data.get("metrics", []):
            category = metric.get("category", "")
            values = metric.get("values", {})
            for name, value in values.items():
                if value is not None:
                    metric_lookup[(category, name)] = float(value)

        for rule in custom_rules:
            key = (rule.metric_category, rule.metric_name)
            current_value = metric_lookup.get(key)

            if current_value is None:
                logger.debug(
                    "Custom rule '%s': metric %s.%s not found in current data",
                    rule.name, rule.metric_category, rule.metric_name,
                )
                continue

            if self._evaluate_condition(current_value, rule.operator, rule.threshold):
                message = (
                    f"## 自定义告警: {rule.name}\n\n"
                    f"- **描述**: {rule.description or '无'}\n"
                    f"- **指标**: {rule.metric_category}.{rule.metric_name}\n"
                    f"- **当前值**: {current_value}\n"
                    f"- **触发条件**: {rule.metric_name} {rule.operator} {rule.threshold}\n"
                    f"- **严重级别**: {rule.severity}\n"
                    f"- **触发时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )
                # 使用 rule.id 作为 alert_type 的一部分以区分不同规则
                alert_type = f"custom_{rule.id}_{rule.metric_name}"
                triggered.append((alert_type, rule.severity, message))
                logger.info(
                    "Custom rule '%s' triggered: %s.%s=%s %s %s",
                    rule.name,
                    rule.metric_category,
                    rule.metric_name,
                    current_value,
                    rule.operator,
                    rule.threshold,
                )

        return triggered

    @staticmethod
    def _evaluate_condition(
        current_value: float, operator: str, threshold: float
    ) -> bool:
        """根据操作符判断当前值是否触发告警条件

        Args:
            current_value: 当前指标值
            operator: 比较操作符 (gt/lt/gte/lte/eq)
            threshold: 告警阈值

        Returns:
            bool: 满足条件返回 True
        """
        if operator == "gt":
            return current_value > threshold
        elif operator == "lt":
            return current_value < threshold
        elif operator == "gte":
            return current_value >= threshold
        elif operator == "lte":
            return current_value <= threshold
        elif operator == "eq":
            return current_value == threshold
        else:
            logger.warning("Unknown operator '%s', defaulting to False", operator)
            return False

    def _get_cooldown_minutes(self, alert_type: str) -> int:
        """获取指定告警类型的冷却时间

        先从内置规则查找，再从自定义规则 cold-start 默认值。

        Args:
            alert_type: 告警类型

        Returns:
            int: 冷却分钟数，未找到时返回默认值 30
        """
        for rule in self._builtin_rules:
            if rule.alert_type == alert_type:
                return rule.cooldown_minutes
        # 对于自定义规则 alert_type 格式为 "custom_{rule_id}_{metric_name}",
        # 默认冷却时间 30 分钟（个别规则的冷却由 _is_in_cooldown 中按规则ID独立处理）
        return 30
