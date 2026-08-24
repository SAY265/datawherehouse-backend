"""Central user/project ownership and membership authorization guard."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.shared.types import EntityID


class ProjectAccessGuard:
    def __init__(
        self,
        project_repository: IProjectRepository,
        member_repository: IProjectMemberRepository,
    ) -> None:
        self._project_repository = project_repository
        self._member_repository = member_repository

    async def verify_project_access(self, project_id: EntityID, user_id: EntityID) -> Project:
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Không tìm thấy dự án.",
            )
        if project.user_id != user_id and not await self._member_repository.is_member(project_id, user_id):
            raise BusinessException(
                code=ErrorCode.PERMISSION_DENIED,
                message="Bạn không có quyền truy cập dự án này.",
            )
        return project
