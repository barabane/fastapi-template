from pydantic import UUID4, EmailStr, Field

from ..common import BaseDTOModel


class LoginCredentialsDTO(BaseDTOModel):
    email: EmailStr
    password: str


class RegisterCredentialsDTO(BaseDTOModel):
    email: EmailStr
    password: str


class NewPasswordCredentialsDTO(BaseDTOModel):
    new_password: str
    repeat_new_password: str


class CreateCredentialsDTO(BaseDTOModel):
    email: EmailStr
    user_id: UUID4
    password_hash: bytes


class UpdateCredentialsDTO(BaseDTOModel):
    password_hash: bytes


class TokenDTO(BaseDTOModel):
    type: str = Field(default="bearer")
    token: str


class RefreshSessionDTO(BaseDTOModel):
    user_id: UUID4
    refresh_token: str
    ua: str
    ip: str
