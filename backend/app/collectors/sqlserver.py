"""
SQL Server 连接管理器
管理到目标 SQL Server 实例的连接池
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import pymssql

from app.config import settings

logger = logging.getLogger(__name__)

_RETRY_MAX = 3


class MSSQLConnectionError(Exception):
    """SQL Server 连接相关异常"""

    pass


class MSSQLConnectionManager:
    """SQL Server 连接管理器

    管理到目标 SQL Server 的连接，使用 pymssql 同步驱动。
    提供连接获取（含重试）、测试和关闭功能。
    支持单实例（默认 settings）和多实例模式。
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ) -> None:
        self.host = host or settings.MSSQL_HOST
        self.port = port or settings.MSSQL_PORT
        self.user = user or settings.MSSQL_USER
        self.password = password or settings.MSSQL_PASSWORD
        self.database = database or settings.MSSQL_DATABASE
        self._connection: Optional[pymssql.Connection] = None

    @staticmethod
    def get_connection_for_instance(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str = "master",
    ) -> "MSSQLConnectionManager":
        """基于指定参数创建一个新的连接管理器实例。

        用于多实例监控场景，不依赖 settings 默认值。

        Args:
            host: SQL Server 主机地址
            port: 端口号
            user: 登录用户名
            password: 登录密码
            database: 数据库名，默认 master

        Returns:
            MSSQLConnectionManager: 配置好的连接管理器实例
        """
        return MSSQLConnectionManager(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )

    def get_connection(self) -> pymssql.Connection:
        """获取 SQL Server 连接

        如果已有可用连接则复用，否则创建新连接。
        创建连接时包含重试机制，最多重试 _RETRY_MAX 次。

        Returns:
            pymssql.Connection: 数据库连接对象

        Raises:
            MSSQLConnectionError: 所有重试均失败时抛出
        """
        if self._connection and self._test_connection_alive():
            return self._connection

        last_exception = None
        for attempt in range(1, _RETRY_MAX + 1):
            try:
                self._connection = pymssql.connect(
                    server=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    timeout=10,
                    login_timeout=10,
                )
                logger.info(
                    "Connected to SQL Server %s:%s/%s (attempt %d/%d)",
                    self.host,
                    self.port,
                    self.database,
                    attempt,
                    _RETRY_MAX,
                )
                return self._connection
            except pymssql.Error as e:
                last_exception = e
                logger.warning(
                    "Failed to connect to SQL Server (attempt %d/%d): %s",
                    attempt,
                    _RETRY_MAX,
                    e,
                )
                if attempt < _RETRY_MAX:
                    import time

                    time.sleep(2 ** attempt)

        raise MSSQLConnectionError(
            f"Could not connect to SQL Server at {self.host}:{self.port} "
            f"after {_RETRY_MAX} attempts: {last_exception}"
        )

    def _test_connection_alive(self) -> bool:
        """测试当前连接是否存活"""
        if self._connection is None:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except (pymssql.Error, Exception):
            return False

    def test_connection(self) -> bool:
        """测试连接是否正常

        Returns:
            bool: 连接正常返回 True，否则返回 False
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            logger.info("SQL Server connection test passed")
            return True
        except (MSSQLConnectionError, pymssql.Error) as e:
            logger.error("SQL Server connection test failed: %s", e)
            return False

    def close(self) -> None:
        """关闭连接"""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.info("SQL Server connection closed")
            except pymssql.Error as e:
                logger.warning("Error closing SQL Server connection: %s", e)
            finally:
                self._connection = None

    @contextmanager
    def cursor(self) -> Generator[pymssql.Cursor, None, None]:
        """获取游标的上下文管理器

        使用示例:
            with manager.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
