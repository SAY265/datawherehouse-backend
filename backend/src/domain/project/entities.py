"""Các thực thể thuộc miền Dự án (Project Entities)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.common.utils.datetime import ensure_utc, utc_now
from src.domain.project.enums import ProjectRole, ProjectStatus
from src.domain.project.rules import validate_project_fields
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class Project(BaseEntity):
    """Thực thể đại diện cho Dự án (Project)."""

    name: str = ""
    requirement: str = ""
    user_id: EntityID = field(default_factory=uuid4)
    description: str | None = None
    domain: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu đầu vào của Dự án."""
        super().__post_init__()
        validate_project_fields(self.name, self.requirement)

    def update_status(self, new_status: ProjectStatus) -> None:
        """Cập nhật trạng thái mới cho dự án."""
        self.status = new_status
        self.mark_updated()

    def update_info(
        self,
        name: str | None = None,
        description: str | None = None,
        domain: str | None = None,
    ) -> None:
        """Cập nhật thông tin dự án."""
        if name is not None:
            new_name = name.strip()
            validate_project_fields(new_name, self.requirement)
            self.name = new_name
        if description is not None:
            self.description = description.strip() or None
        if domain is not None:
            self.domain = domain.strip() or self.domain
        self.mark_updated()

    def create_owner_member(self) -> "ProjectMember":
        """Tạo thực thể thành viên dự án với vai trò OWNER cho người tạo dự án."""
        return ProjectMember(
            project_id=self.id,
            user_id=self.user_id,
            role=ProjectRole.OWNER,
        )


@dataclass(eq=False)
class ProjectMember(BaseEntity):
    """Thực thể đại diện cho Thành viên tham gia Dự án."""

    project_id: EntityID = field(default_factory=uuid4)
    user_id: EntityID = field(default_factory=uuid4)
    role: ProjectRole = ProjectRole.MEMBER
    joined_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Đảm bảo mốc thời gian joined_at có timezone UTC."""
        super().__post_init__()
        self.joined_at = ensure_utc(self.joined_at)
