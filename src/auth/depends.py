from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import EmailStr

from ..auth import AuthRepository, auth_repository_depends
from ..users import User, UserRepository, user_repository_depends
from ..utils import decode_token


async def check_user_auth(
    request: Request,
    response: Response,
    token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    user_repository: UserRepository = user_repository_depends,
    auth_repository: AuthRepository = auth_repository_depends,
):
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Вы не авторизованы")

    try:
        payload = decode_token(token.credentials)

        return await user_repository.find_one(id=payload["sub"])
    except ExpiredSignatureError:
        if not (refresh_token := request.cookies.get("refresh_token")):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Вы не авторизованы")

        try:
            payload = decode_token(refresh_token)

            await auth_repository.delete_refresh_session(refresh_token)

            await auth_repository.add_refresh_session(
                request, response, payload["sub"], payload["email"]
            )

            return await user_repository.find_one(id=payload["sub"])

        except ExpiredSignatureError:
            await auth_repository.delete_refresh_session(refresh_token)
            response.delete_cookie("refresh_token")
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    except PyJWTError:
        response.delete_cookie("refresh_token")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Вы не авторизованы")


user_auth_depends: User = Depends(check_user_auth)


async def check_email(
    email: EmailStr,
    auth_repository: AuthRepository = auth_repository_depends,
) -> EmailStr:
    if not await auth_repository.find_one_or_none(email=email):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Пользователя с таким email не существует"
        )

    return email


email_depends: EmailStr = Depends(check_email)
