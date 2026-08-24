"""PostgreSQL repository cho JWT revocation."""

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.user.i_revoked_token_repository import IRevokedTokenRepository
from src.domain.user.revoked_token import RevokedToken
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.revoked_token_mapper import RevokedTokenMapper
from src.infrastructure.database.models.revoked_token import RevokedTokenModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresRevokedTokenRepository(IRevokedTokenRepository):
    """Persist revoked access-token JTIs in PostgreSQL across restarts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, RevokedTokenModel, RevokedTokenMapper)

    @override
    @translate_database_errors
    async def exists(self, jti: str) -> bool:
        statement = select(RevokedTokenModel.id).where(RevokedTokenModel.jti == jti).limit(1)
        return (await self._session.scalar(statement)) is not None

    @override
    async def save(self, token: RevokedToken) -> None:
        await self._crud.save(token)

    @override
    @translate_database_errors
    async def delete_expired(self, now: datetime) -> None:
        await self._session.execute(
            delete(RevokedTokenModel).where(RevokedTokenModel.expires_at <= now)
        )
