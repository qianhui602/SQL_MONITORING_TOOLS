"""密码加密/解密服务

使用 Fernet 对称加密（cryptography 库）对 SQL Server 密码进行加密存储。
解密失败时兼容旧的明文密码（直接返回原值），无需数据迁移。
"""

from cryptography.fernet import Fernet

from app.config import settings

_fernet = None


def _get_fernet() -> Fernet:
    """获取 Fernet 实例（懒加载）"""
    global _fernet
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        _fernet = Fernet(key)
    return _fernet


def encrypt_password(plaintext: str) -> str:
    """加密密码

    Args:
        plaintext: 明文密码

    Returns:
        加密后的密文字符串，空输入返回空字符串
    """
    if not plaintext:
        return ""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_password(ciphertext: str) -> str:
    """解密密码

    兼容旧的明文密码：如果解密失败（说明是未加密的明文），直接返回原值。

    Args:
        ciphertext: 密文字符串（或旧的明文密码）

    Returns:
        解密后的明文密码，空输入返回空字符串
    """
    if not ciphertext:
        return ""
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except Exception:
        # 解密失败（可能是旧的明文密码），直接返回原值
        return ciphertext
