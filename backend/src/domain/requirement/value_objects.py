"""Value objects của Requirement domain."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.requirement.rules import normalize_requirement_fields
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class RequirementDetails(BaseValueObject):
    """Nội dung có thể chỉnh sửa của một Requirement."""

    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority

    def __post_init__(self) -> None:
        """Chuẩn hóa nội dung và enum tại một điểm duy nhất."""
        title, description = normalize_requirement_fields(self.title, self.description)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)
        object.__setattr__(
            self,
            "type",
            normalize_str_enum(self.type, RequirementType, ErrorCode.VALIDATION_ERROR),
        )
        object.__setattr__(
            self,
            "priority",
            normalize_str_enum(
                self.priority, RequirementPriority, ErrorCode.VALIDATION_ERROR
            ),
        )
