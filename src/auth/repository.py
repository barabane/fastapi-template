from fastapi import Depends, Request, Response
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..common import BaseRepository
from ..config import config
from ..databases.postgres import session_depends
from ..utils import gen_tokens_pair
from .dtos import (CreateCredentialsDTO, RefreshSessionDTO, TokenDTO,
                   UpdateCredentialsDTO)
from .models import AuthCredential, RefreshSession


class AuthRepository(
    BaseRepository[AuthCredential, CreateCredentialsDTO, UpdateCredentialsDTO, None]
):
    async def add_refresh_session(
        self,
        request: Request,
        response: Response,
        user_id,
        user_email,
    ) -> TokenDTO:
        access_token, refresh_token = gen_tokens_pair(
            response=response,
            payload={"sub": str(user_id), "email": user_email},
            key=config.SECRET,
        )

        await self._session.execute(
            insert(RefreshSession).values(
                **RefreshSessionDTO(
                    user_id=user_id,
                    refresh_token=refresh_token,
                    ua=request.headers["user-agent"],
                    ip=request.headers["host"],
                ).model_dump()
            )
        )

        return TokenDTO(token=access_token)

    async def delete_refresh_session(self, refresh_token: str):
        await self._session.execute(
            delete(RefreshSession).where(RefreshSession.refresh_token == refresh_token)
        )


async def get_auth_repository(
    session: AsyncSession = session_depends,
) -> AuthRepository:
    return AuthRepository(model=AuthCredential, session=session)


auth_repository_depends: AuthRepository = Depends(get_auth_repository)
