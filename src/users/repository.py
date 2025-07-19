from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..common import BaseRepository
from ..databases.postgres import session_depends
from .dtos import CreateUserDTO, GetUserDTO, UpdateUserDTO
from .models import User


class UserRepository(
    BaseRepository[User, CreateUserDTO, UpdateUserDTO, GetUserDTO]
): ...


async def get_user_repository(
    session: AsyncSession = session_depends,
) -> UserRepository:
    return UserRepository(User, session)


user_repository_depends: UserRepository = Depends(get_user_repository)
