"""Mapper giữa RevokedToken domain và ORM."""

from src.domain.user.revoked_token import RevokedToken
from src.infrastructure.database.models.revoked_token import RevokedTokenModel


class RevokedTokenMapper:
    """Map revoked-token entities to and from their SQLAlchemy model."""

    @staticmethod
    def to_domain(model: RevokedTokenModel) -> RevokedToken:
        return RevokedToken(
            id=model.id,
            jti=model.jti,
            user_id=model.user_id,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: RevokedToken) -> RevokedTokenModel:
        return RevokedTokenModel(
            id=entity.id,
            jti=entity.jti,
            user_id=entity.user_id,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: RevokedTokenModel, entity: RevokedToken) -> RevokedTokenModel:
        model.expires_at = entity.expires_at
        model.updated_at = entity.updated_at
        return model
