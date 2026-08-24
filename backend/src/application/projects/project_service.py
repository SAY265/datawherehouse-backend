"""Application service duy nhất của module Project."""

from typing import TYPE_CHECKING

from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.output import DataModelOutput
from src.application.projects.i_project_service import IProjectService
from src.application.projects.initial_dbml_generator import generate_initial_dbml
from src.application.projects.input import (
    CreateProjectInput,
    LoadProjectSourceInput,
    UpdateProjectInput,
)
from src.application.projects.output import (
    ProjectDetailOutput,
    ProjectOutput,
    ProjectSummaryOutput,
)
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.domain.project.repository import IProjectRepository
from src.domain.shared.types import EntityID
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.security.pii_masking import mask_text
from typing_extensions import override

if TYPE_CHECKING:
    from src.infrastructure.storage.session_data_manager import SessionDataManager


class ProjectService(IProjectService):
    """Điểm hiện thực tập trung cho các use case Project."""

    def __init__(
        self,
        project_repository: IProjectRepository,
        data_model_repository: IDataModelRepository,
        unit_of_work: IUnitOfWork,
        session_data_manager: "SessionDataManager | None" = None,
        access_guard: ProjectAccessGuard | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._data_model_repository = data_model_repository
        self._unit_of_work = unit_of_work
        self._session_data_manager = session_data_manager
        self._access_guard = access_guard

    @override
    async def create_project(self, data: CreateProjectInput, user_id: EntityID) -> ProjectOutput:
        """Tạo project thật để các bước Modeling và Sandbox dùng cùng UUID."""
        safe_description = data.business_description.strip()
        if data.is_masking_enabled:
            safe_description = mask_text(safe_description)
        requirement = safe_description or (
            f"Phân tích dữ liệu thuộc miền {data.domain.strip() or 'general'}."
        )
        project_name = data.name.strip() if data.name else ""
        if not project_name:
            raise BusinessException(
                code=ErrorCode.INVALID_PROJECT_NAME,
                message="Tên dự án không được để trống.",
            )
        existing_projects = await self._project_repository.list_by_user(user_id)
        if any(p.name.strip().lower() == project_name.lower() for p in existing_projects):
            raise BusinessException(
                code=ErrorCode.PROJECT_NAME_ALREADY_EXISTS,
                message=f"Tên dự án '{project_name}' đã tồn tại. Vui lòng chọn tên khác.",
            )
        project = await self._project_repository.save(
            Project(
                name=project_name,
                requirement=requirement,
                user_id=user_id,
                description=safe_description or None,
                domain=data.domain.strip() or "general",
            )
        )
        # Lưu dữ liệu cấu trúc nguồn nạp từ Frontend vào thư mục data_AI để AI phân tích
        if self._session_data_manager is not None:
            try:
                user_data_manager = self._session_data_manager.scoped(str(user_id))
                user_data_manager.save_source_tables_metadata(
                    domain=data.domain,
                    source_tables=list(data.source_tables),
                    business_description=safe_description,
                    is_masking_enabled=data.is_masking_enabled,
                )
            except Exception:
                pass

        initial_dbml = await generate_initial_dbml(
            domain=data.domain,
            description=safe_description,
            tables=list(data.source_tables),
            target_dialect=data.target_dialect,
        )
        await self._data_model_repository.save(DataModel(project_id=project.id, dbml=initial_dbml))
        await self._unit_of_work.commit()
        return ProjectOutput(
            project_id=project.id,
            name=project.name,
            domain=project.domain or "general",
            target_dialect=data.target_dialect,
            status=project.status.value,
            created_at=project.created_at,
        )

    @override
    async def list_projects(self, user_id: EntityID) -> list[ProjectSummaryOutput]:
        projects = await self._project_repository.list_by_user(user_id)
        return [
            ProjectSummaryOutput(
                project_id=project.id,
                name=project.name,
                domain=project.domain or "general",
                status=project.status.value,
                updated_at=project.updated_at,
            )
            for project in projects
        ]

    @override
    async def get_project(self, project_id: EntityID, user_id: EntityID) -> ProjectDetailOutput:
        """Lấy chi tiết dự án thuộc sở hữu của user."""
        project = (
            await self._access_guard.verify_project_access(project_id, user_id)
            if self._access_guard is not None
            else await self._project_repository.get_by_id(project_id)
        )
        if project is None or (self._access_guard is None and project.user_id != user_id):
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Không tìm thấy dự án hoặc bạn không có quyền truy cập.",
            )
        data_model = await self._data_model_repository.get_by_project_id(project_id)
        revision = data_model.revision if data_model is not None else 1
        return ProjectDetailOutput(
            project_id=project.id,
            name=project.name,
            domain=project.domain or "general",
            description=project.description,
            requirement=project.requirement,
            status=project.status.value,
            target_dialect="postgresql",
            created_at=project.created_at,
            updated_at=project.updated_at,
            revision=revision,
        )

    @override
    async def update_project(
        self, data: UpdateProjectInput, user_id: EntityID
    ) -> ProjectDetailOutput:
        """Cập nhật thông tin dự án."""
        project = (
            await self._access_guard.verify_project_access(data.project_id, user_id)
            if self._access_guard is not None
            else await self._project_repository.get_by_id(data.project_id)
        )
        if project is None or (self._access_guard is None and project.user_id != user_id):
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Không tìm thấy dự án hoặc bạn không có quyền chỉnh sửa.",
            )
        if data.name is not None:
            new_name = data.name.strip()
            if not new_name:
                raise BusinessException(
                    code=ErrorCode.INVALID_PROJECT_NAME,
                    message="Tên dự án không được để trống.",
                )
            if new_name.lower() != project.name.strip().lower():
                existing_projects = await self._project_repository.list_by_user(user_id)
                if any(
                    str(p.id) != str(project.id) and p.name.strip().lower() == new_name.lower()
                    for p in existing_projects
                ):
                    raise BusinessException(
                        code=ErrorCode.PROJECT_NAME_ALREADY_EXISTS,
                        message=f"Tên dự án '{new_name}' đã tồn tại. Vui lòng chọn tên khác.",
                    )

        project.update_info(
            name=data.name,
            description=data.description,
            domain=data.domain,
        )
        if data.status:
            try:
                project.update_status(ProjectStatus(data.status))
            except ValueError:
                pass

        saved = await self._project_repository.save(project)
        await self._unit_of_work.commit()
        data_model = await self._data_model_repository.get_by_project_id(data.project_id)
        revision = data_model.revision if data_model is not None else 1
        return ProjectDetailOutput(
            project_id=saved.id,
            name=saved.name,
            domain=saved.domain or "general",
            description=saved.description,
            requirement=saved.requirement,
            status=saved.status.value,
            target_dialect="postgresql",
            created_at=saved.created_at,
            updated_at=saved.updated_at,
            revision=revision,
        )

    @override
    async def delete_project(self, project_id: EntityID, user_id: EntityID) -> bool:
        """Xóa dự án và các tài nguyên phụ thuộc."""
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            return False
        if project.user_id != user_id:
            raise BusinessException(
                code=ErrorCode.PERMISSION_DENIED,
                message="Bạn không có quyền xóa dự án này.",
            )
        deleted = await self._project_repository.delete(project_id)
        await self._unit_of_work.commit()
        return deleted

    @override
    async def load_source_schema(
        self, data: LoadProjectSourceInput, user_id: EntityID
    ) -> DataModelOutput:
        """Sinh lại Data Model từ schema nguồn sau khi project đã tồn tại."""
        project = (
            await self._access_guard.verify_project_access(data.project_id, user_id)
            if self._access_guard is not None
            else await self._project_repository.get_by_id(data.project_id)
        )
        if project is None or (self._access_guard is None and project.user_id != user_id):
            raise BusinessException(
                code=ErrorCode.PERMISSION_DENIED,
                message="Bạn không có quyền nạp dữ liệu vào dự án này.",
            )
        current = await self._data_model_repository.get_by_project_id(data.project_id)
        if current is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )

        if self._session_data_manager is not None:
            self._session_data_manager.scoped(str(user_id)).save_source_tables_metadata(
                domain=project.domain or "general",
                source_tables=list(data.source_tables),
                business_description=project.description or "",
                is_masking_enabled=data.is_masking_enabled,
            )

        dbml = await generate_initial_dbml(
            domain=project.domain or "general",
            description=project.description or "",
            tables=list(data.source_tables),
            target_dialect=data.target_dialect,
        )
        base_revision = current.revision
        current.update_dbml(dbml, base_revision)
        updated = await self._data_model_repository.update_if_revision_matches(
            current, base_revision
        )
        if updated is None:
            raise BusinessException(
                code=ErrorCode.REVISION_CONFLICT,
                message="Data Model đã thay đổi trong lúc nạp dữ liệu.",
            )
        await self._unit_of_work.commit()
        return DataModelOutput.from_domain(updated)
