from pydantic import UUID4, EmailStr, Field

from ..common import BaseDTOModel
from .enums import UserStatus


class GetUserDTO(BaseDTOModel):
    id: UUID4
    status: UserStatus


class CreateUserDTO(BaseDTOModel):
    email: EmailStr
    status: UserStatus = Field(default=UserStatus.NOT_ACTIVE)


class UpdateUserDTO(BaseDTOModel):
    status: UserStatus
