"""Policy ánh xạ entity PII sang operator của Presidio Anonymizer."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from src.infrastructure.security.pii.pii_entities import (
    CREDIT_CARD,
    EMAIL_ADDRESS,
    LOCATION,
    PERSON,
    PHONE_NUMBER,
    VN_CCCD,
    VN_CMND,
)

OperatorParameter = str | int | bool


@dataclass(frozen=True, slots=True)
class PiiOperator:
    """Cấu hình một operator anonymization của Presidio."""

    name: str = "replace"
    parameters: Mapping[str, OperatorParameter] = field(default_factory=dict)

    @classmethod
    def replace(cls, replacement: str) -> "PiiOperator":
        """Tạo operator thay entity bằng placeholder cố định."""
        return cls("replace", MappingProxyType({"new_value": replacement}))


@dataclass(frozen=True, slots=True)
class PiiMaskingPolicy:
    """Quy định entity cần che và operator tương ứng."""

    operators: Mapping[str, PiiOperator]

    @property
    def entities(self) -> tuple[str, ...]:
        """Trả danh sách entity được policy cho phép che."""
        return tuple(self.operators)


DEFAULT_MASKING_POLICY = PiiMaskingPolicy(
    MappingProxyType(
        {
            EMAIL_ADDRESS: PiiOperator.replace("<EMAIL>"),
            PHONE_NUMBER: PiiOperator.replace("<PHONE>"),
            CREDIT_CARD: PiiOperator.replace("<PAYMENT_CARD>"),
            PERSON: PiiOperator.replace("<PERSON>"),
            LOCATION: PiiOperator.replace("<LOCATION>"),
            VN_CCCD: PiiOperator.replace("<ID_NUMBER>"),
            VN_CMND: PiiOperator.replace("<ID_NUMBER>"),
        }
    )
)
