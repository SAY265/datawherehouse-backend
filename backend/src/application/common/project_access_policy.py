"""Chính sách phân quyền dự án dùng chung cho các application service."""

from dataclasses import dataclass
from typing import NoReturn

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectRole
from src.domain.project.i_project_member_repository import IProjectMemberRepository
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ProjectAccess:
    """Kết quả xác minh quyền truy cập một dự án."""

    project: Project
    can_edit: bool


class ProjectAccessPolicy:
    """Xác minh quyền MEMBER hoặc OWNER mà không phụ thuộc HTTP."""

    def __init__(
        self,
        projects: IProjectRepository,
        members: IProjectMemberRepository,
        actor_id: EntityID,
    ) -> None:
        self._projects = projects
        self._members = members
        self.actor_id = actor_id

    async def require_member(self, project_id: EntityID) -> ProjectAccess:
        """Trả dự án và quyền chỉnh sửa nếu actor là thành viên.

        Raises:
            BusinessException: Khi dự án không tồn tại hoặc actor không có quyền đọc.
        """
        project = await self._get_project(project_id)
        if project.user_id == self.actor_id:
            return ProjectAccess(project, True)
        membership = await self._members.get_by_project_and_user(project_id, self.actor_id)
        if membership is None:
            _raise_permission_denied()
        return ProjectAccess(project, membership.role == ProjectRole.OWNER)

    async def require_owner(self, project_id: EntityID) -> Project:
        """Trả dự án nếu actor có quyền OWNER.

        Raises:
            BusinessException: Khi dự án không tồn tại hoặc actor không phải OWNER.
        """
        access = await self.require_member(project_id)
        if not access.can_edit:
            _raise_permission_denied()
        return access.project

    async def _get_project(self, project_id: EntityID) -> Project:
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Dự án không tồn tại.",
            )
        return project


def _raise_permission_denied() -> NoReturn:
    raise BusinessException(
        code=ErrorCode.PERMISSION_DENIED,
        message="Bạn không có quyền thực hiện thao tác trên dự án này.",
    )
