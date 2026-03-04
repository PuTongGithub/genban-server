import bcrypt


def hashPassword(password: str) -> str:
    # 生成密码哈希
    passwordBytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwordBytes, salt)
    return hashed.decode("utf-8")


def verifyPassword(password: str, passwordHash: str) -> bool:
    # 校验密码
    passwordBytes = password.encode("utf-8")
    hashBytes = passwordHash.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashBytes)
