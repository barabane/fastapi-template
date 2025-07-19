from uuid import uuid4

from pydantic import UUID4
from sqlalchemy.orm import Mapped, mapped_column

from ..common import BaseDBModel
from .enums import UserStatus


class User(BaseDBModel):
    __tablename__ = "users"

    id: Mapped[UUID4] = mapped_column(primary_key=True, default=lambda: uuid4())
    email: Mapped[str] = mapped_column(unique=True)
    status: Mapped[int] = mapped_column(default=UserStatus.NOT_ACTIVE)
