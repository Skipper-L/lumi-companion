from pwdlib import PasswordHash

# 使用 pwdlib 推荐的 Argon2 密码哈希配置
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    将用户原始密码转换成不可逆的哈希文本。
    数据库只保存这个结果，不保存原始密码。
    """
    return password_hash.hash(password)


def verify_password(password: str, password_hash_value: str) -> bool:
    """
    判断用户输入的密码，
    是否与数据库中保存的密码哈希匹配。
    """
    return password_hash.verify(
        password,
        password_hash_value,
    )