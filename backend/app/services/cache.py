"""
全局缓存服务
基于 TTLCache 实现的内存缓存，支持用户缓存、配置缓存、实例缓存、指标缓存。
"""

import time
from typing import Any, Dict, Optional


class TTLCache:
    """简单的 TTL 缓存实现"""

    def __init__(self, ttl_seconds: int):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，过期返回 None"""
        item = self._cache.get(key)
        if not item:
            return None
        if time.time() > item["expire_at"]:
            del self._cache[key]
            return None
        return item["value"]

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """设置缓存值"""
        ttl = ttl_seconds if ttl_seconds is not None else self._ttl
        self._cache[key] = {
            "value": value,
            "expire_at": time.time() + ttl,
        }

    def delete(self, key: str) -> None:
        """删除缓存"""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {"size": len(self._cache)}


# 全局缓存实例
_user_cache = TTLCache(ttl_seconds=300)
_config_cache = TTLCache(ttl_seconds=60)
_instance_cache = TTLCache(ttl_seconds=120)
_metrics_cache = TTLCache(ttl_seconds=60)


# ===== 用户缓存 =====


def get_user_cache() -> TTLCache:
    return _user_cache


def cache_user(user_id: int, user_data: Any) -> None:
    _user_cache.set(f"user:{user_id}", user_data)


def get_cached_user(user_id: int) -> Optional[Any]:
    return _user_cache.get(f"user:{user_id}")


def invalidate_user_cache(user_id: int) -> None:
    _user_cache.delete(f"user:{user_id}")


# ===== 配置缓存 =====


def get_config_cache() -> TTLCache:
    return _config_cache


def cache_config(config_key: str, config_value: Any) -> None:
    _config_cache.set(f"config:{config_key}", config_value)


def cache_configs(configs: Dict[str, Any]) -> None:
    for key, value in configs.items():
        _config_cache.set(f"config:{key}", value)


def get_cached_config(config_key: str) -> Optional[Any]:
    return _config_cache.get(f"config:{key}")


def get_cached_configs() -> Optional[Dict[str, Any]]:
    result = {}
    for key in list(_config_cache._cache.keys()):
        if key.startswith("config:"):
            value = _config_cache.get(key)
            if value is not None:
                result[key.replace("config:", "", 1)] = value
    return result if result else None


def invalidate_config_cache(config_key: Optional[str] = None) -> None:
    if config_key:
        _config_cache.delete(f"config:{config_key}")
    else:
        _config_cache.clear()


# ===== 实例缓存 =====


def get_instance_cache() -> TTLCache:
    return _instance_cache


def cache_instances(instances: Any) -> None:
    _instance_cache.set("instances:active", instances)


def get_cached_instances() -> Optional[Any]:
    return _instance_cache.get("instances:active")


def invalidate_instance_cache() -> None:
    _instance_cache.clear()


# ===== 指标缓存 =====


def get_metrics_cache() -> TTLCache:
    return _metrics_cache


def cache_metrics(key: str, metrics: Any) -> None:
    _metrics_cache.set(f"metrics:{key}", metrics)


def get_cached_metrics(key: str) -> Optional[Any]:
    return _metrics_cache.get(f"metrics:{key}")


def invalidate_metrics_cache(key: Optional[str] = None) -> None:
    if key:
        _metrics_cache.delete(f"metrics:{key}")
    else:
        _metrics_cache.clear()
