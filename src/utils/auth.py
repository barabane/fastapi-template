import random
import time

import jwt
from fastapi import Response
from pydantic import EmailStr

from src.config import config

from ..databases.redis import redis_connection
from .smtp import send_email


def gen_tokens_pair(response: Response, payload: dict, key: str) -> tuple[str, str]:
    if not payload.get("sub"):
        raise ValueError("sub is required")

    payload["exp"] = time.time() + 1800
    access_token = jwt.encode(payload=payload, key=key, algorithm=config.ALGORITHM)
    response.headers["Authorization"] = f"bearer {access_token}"

    payload["exp"] = time.time() + 3600
    refresh_token = jwt.encode(payload=payload, key=key, algorithm=config.ALGORITHM)
    response.set_cookie(
        "refresh_token", refresh_token, max_age=payload["exp"], samesite="lax"
    )

    return access_token, refresh_token


def decode_token(token: str):
    return jwt.decode(token, config.SECRET, config.ALGORITHM)


async def send_email_code(email: EmailStr):
    code = random.randint(1_000_00, 9_999_99)
    await redis_connection.setex(email, 120, f"{code}")
    send_email(f"confirmation:{email}", f"Код: {code}")


async def send_reset_password_email_code(email: EmailStr):
    code = random.randint(1_000_00, 9_999_99)
    await redis_connection.setex(f"reset:{email}", 300, f"{code}")
    send_email(email, f"Код для сброса пароля: {code}")
