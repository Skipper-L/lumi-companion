import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError

# 读取 backend/.env 文件
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "10080")
)

if not SECRET_KEY:
    raise RuntimeError(
        "没有读取到 JWT_SECRET_KEY，请检查 backend/.env 文件。"
    )


def create_access_token(user_id: int, username: str) -> str:
    """为登录成功的用户创建 JWT Token。"""
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire_time,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    验证并解析 Token。

    Token 无效、被修改或过期时，直接返回 401 错误。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录状态无效或已过期，请重新登录",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        username = payload.get("username")

        if user_id is None or username is None:
            raise credentials_exception

        return {
            "user_id": int(user_id),
            "username": username,
        }

    except (InvalidTokenError, ValueError):
        raise credentials_exception