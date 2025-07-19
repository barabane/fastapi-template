from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import EmailStr

from src.auth import (AuthService, LoginCredentialsDTO,
                      NewPasswordCredentialsDTO, RegisterCredentialsDTO,
                      TokenDTO, auth_service_depends, email_depends,
                      user_auth_depends)
from src.users import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign-up")
async def sign_up(
    response: Response,
    request: Request,
    credentials: RegisterCredentialsDTO,
    auth_service: AuthService = auth_service_depends,
) -> TokenDTO:
    return await auth_service.sign_up(request, response, credentials)


@router.post("/send-code")
async def send_code(
    email: EmailStr = email_depends, auth_service: AuthService = auth_service_depends
) -> None:
    await auth_service.send_code(email)


@router.post("/confirm-email")
async def confirm_email(
    code: int,
    email: EmailStr = email_depends,
    auth_service: AuthService = auth_service_depends,
) -> None:
    return await auth_service.confirm_email(email, code)


@router.post("/sign-in")
async def sign_in(
    response: Response,
    request: Request,
    credentials: LoginCredentialsDTO,
    auth_service: AuthService = auth_service_depends,
) -> TokenDTO:
    if request.headers.get("Authorization"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Вы уже вошли")

    return await auth_service.login(request, response, credentials)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: User = user_auth_depends,
    auth_service: AuthService = auth_service_depends,
):
    await auth_service.logout(request.cookies.get("refresh_token"))  # type: ignore
    response.delete_cookie("refresh_token")


@router.post("/reset-password")
async def reset_password(
    email: EmailStr = email_depends, auth_service: AuthService = auth_service_depends
):
    return await auth_service.send_reset_password_code(email)


@router.post("/confirm-reset")
async def confirm_reset(
    code: int,
    credentials_dto: NewPasswordCredentialsDTO,
    email: EmailStr = email_depends,
    auth_service: AuthService = auth_service_depends,
):
    return await auth_service.confirm_reset_password(email, code, credentials_dto)


@router.post("/update-password")
async def update_password(
    old_password: str,
    credentials_dto: NewPasswordCredentialsDTO,
    user: User = user_auth_depends,
    auth_service: AuthService = auth_service_depends,
) -> Response:
    return await auth_service.update_password(user.id, old_password, credentials_dto)
