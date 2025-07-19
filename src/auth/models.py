from uuid import uuid4

from pydantic import UUID4
from sqlalchemy.orm import Mapped, mapped_column

from ..common import BaseDBModel


class RefreshSession(BaseDBModel):
    __tablename__ = "refresh_sessions"

    id: Mapped[UUID4] = mapped_column(primary_key=True, default=lambda: uuid4())
    user_id: Mapped[UUID4] = mapped_column()
    refresh_token: Mapped[str] = mapped_column()
    ua: Mapped[str] = mapped_column()
    ip: Mapped[str] = mapped_column()


class AuthCredential(BaseDBModel):
    __tablename__ = "auth_credentials"

    id: Mapped[UUID4] = mapped_column(primary_key=True, default=lambda: uuid4())
    user_id: Mapped[UUID4] = mapped_column()
    password_hash: Mapped[bytes] = mapped_column()
    email: Mapped[str] = mapped_column()
