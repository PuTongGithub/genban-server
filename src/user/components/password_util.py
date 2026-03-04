import bcrypt
from src.user.exceptions import WeakPasswordException


def hash_password(password: str) -> str:
    # 生成密码哈希
    passwordBytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwordBytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, passwordHash: str) -> bool:
    # 校验密码
    passwordBytes = password.encode("utf-8")
    hashBytes = passwordHash.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashBytes)


def validate_password(password: str) -> None:
    # 校验密码强度
    if len(password) < 6:
        raise WeakPasswordException("密码最少需要6位字符")
