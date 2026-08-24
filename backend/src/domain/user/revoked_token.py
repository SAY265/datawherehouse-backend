"""Domain entity ghi nhận một JWT đã bị thu hồi."""

from dataclasses import dataclass
from datetime import datetime

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import ensure_utc
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class RevokedToken(BaseEntity):
    jti: str
    user_id: EntityID
    expires_at: datetime

    def __post_init__(self) -> None:
        super().__post_init__()
        self.jti = self.jti.strip()
        if not self.jti:
            raise BusinessException(ErrorCode.TOKEN_INVALID, "Token identifier không hợp lệ.")
        self.expires_at = ensure_utc(self.expires_at)

