"""Input model cho các thao tác Requirement."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ListRequirementsInput:
    """Dữ liệu đầu vào để liệt kê yêu cầu của một dự án."""

    project_id: EntityID
