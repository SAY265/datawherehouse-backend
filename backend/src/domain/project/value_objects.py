"""Value objects của miền Dự án."""

from dataclasses import dataclass

from src.common.utils.string import safe_strip
from src.domain.project.project_details_rules import (
    normalize_project_domain,
    normalize_project_name,
    normalize_project_requirement,
)
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class ProjectDetails(BaseValueObject):
    """Thông tin nghiệp vụ có thể chỉnh sửa của dự án."""

    name: str
    requirement: str | None = None
    domain: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa dữ liệu ngay khi tạo value object."""
        object.__setattr__(self, "name", normalize_project_name(self.name))
        object.__setattr__(
            self,
            "requirement",
            normalize_project_requirement(self.requirement),
        )
        object.__setattr__(self, "domain", normalize_project_domain(self.domain))
        object.__setattr__(self, "description", safe_strip(self.description))
