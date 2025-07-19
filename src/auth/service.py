import bcrypt
from fastapi import Depends, HTTPException, Request, Response, status
from pydantic import UUID4, EmailStr

from ..common import BaseService
from ..databases.redis import redis_connection
from ..users import (CreateUserDTO, UpdateUserDTO, UserRepository, UserStatus,
                     user_repository_depends)
from ..utils import send_email_code, send_reset_password_email_code
from .dtos import (CreateCredentialsDTO, LoginCredentialsDTO,
                   NewPasswordCredentialsDTO, RegisterCredentialsDTO, TokenDTO,
                   UpdateCredentialsDTO)
from .repository import AuthRepository, auth_repository_depends


class AuthService(BaseService):
    def __init__(
        self, auth_repository: AuthRepository, user_repository: UserRepository
    ):
        self.auth_repository: AuthRepository = auth_repository
        self.user_repository: UserRepository = user_repository
        super().__init__()

    async def sign_up(
        self,
        request: Request,
        response: Response,
        credentials_dto: RegisterCredentialsDTO,
    ) -> TokenDTO:
        credentials = await self.auth_repository.find_one_or_none(
            email=credentials_dto.email
        )

        if credentials:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Пользователь с таким email уже существует"
            )

        password_hash = bcrypt.hashpw(
            credentials_dto.password.encode(), bcrypt.gensalt()
        )

        user = await self.user_repository.insert_one(
            CreateUserDTO(email=credentials_dto.email, status=UserStatus.NOT_ACTIVE)
        )

        credentials = await self.auth_repository.insert_one(
            CreateCredentialsDTO.model_validate(
                {
                    "email": user.email,
                    "password_hash": password_hash,
                    "user_id": user.id,
                }
            )
        )

        await send_email_code(credentials.email)

        return await self.auth_repository.add_refresh_session(
            request, response, user.id, user.email
        )

    async def login(
        self, request: Request, response: Response, credentials_dto: LoginCredentialsDTO
    ) -> TokenDTO:
        credentials = await self.auth_repository.find_one_or_none(
            email=credentials_dto.email
        )

        if not credentials:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Пользователя с таким email не существует"
            )

        if not bcrypt.checkpw(
            credentials_dto.password.encode(), credentials.password_hash
        ):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Неправильный логин/пароль"
            )

        return await self.auth_repository.add_refresh_session(
            request, response, credentials.user_id, credentials.email
        )

    async def logout(self, refresh_token: str) -> None:
        await self.auth_repository.delete_refresh_session(refresh_token)

    async def confirm_email(self, email: EmailStr, code: int) -> None:
        actual_code = await redis_connection.getdel(email)

        if actual_code is not None and int(actual_code) != code:
            raise HTTPException(status.HTTP_409_CONFLICT, "Неправильный код")

        await self.user_repository.update_one(UpdateUserDTO(status=UserStatus.ACTIVE))

    async def send_code(self, email: EmailStr):
        code = await redis_connection.get(f"confirmation:{email}")

        if code:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Новый код можно получить через: {await redis_connection.ttl(email)} с.",
            )

        await send_email_code(email)

    async def send_reset_password_code(self, email: EmailStr):
        code = await redis_connection.get(f"reset:{email}")

        if code:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Запросить повторный сброс пароля можно через: {await redis_connection.ttl(email)} с.",
            )

        await send_reset_password_email_code(email)

    async def confirm_reset_password(
        self, email: EmailStr, code: int, credentials_dto: NewPasswordCredentialsDTO
    ) -> Response:
        actual_code = await redis_connection.get(f"reset:{email}")

        if actual_code != code:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверный код")

        if credentials_dto.new_password != credentials_dto.repeat_new_password:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пароли не совпадают")

        await redis_connection.getdel(f"reset:{email}")

        await self.auth_repository.update_one(
            UpdateCredentialsDTO(
                password_hash=bcrypt.hashpw(
                    credentials_dto.new_password.encode(), bcrypt.gensalt()
                )
            )
        )

        return Response("Пароль успешно изменен")

    async def update_password(
        self,
        user_id: UUID4,
        old_password: str,
        credentials_dto: NewPasswordCredentialsDTO,
    ) -> Response:
        credentials = await self.auth_repository.find_one(user_id=user_id)

        if credentials_dto.new_password != credentials_dto.repeat_new_password:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пароли не совпадают")

        if not bcrypt.checkpw(old_password.encode(), credentials.password_hash):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Неправильный старый пароль"
            )

        await self.auth_repository.update_one(
            UpdateCredentialsDTO(
                password_hash=bcrypt.hashpw(
                    credentials_dto.new_password.encode(), bcrypt.gensalt()
                )
            )
        )

        return Response("Пароль успешно изменен")


async def get_auth_service(
    auth_repository: AuthRepository = auth_repository_depends,
    user_repository: UserRepository = user_repository_depends,
) -> AuthService:
    return AuthService(auth_repository, user_repository)


auth_service_depends: AuthService = Depends(get_auth_service)
