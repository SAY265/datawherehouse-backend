"""Persistence phase tách biệt khỏi các LLM invocation của workflow."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.project.entities import Project
from src.domain.shared.types import EntityID


class WorkflowPersistence:
    """Persist kết quả sau khi kiểm tra lại các revision liên quan."""

    def __init__(
        self,
        models: IDataModelRepository,
        changes: IDataModelChangeRepository,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
    ) -> None:
        self._models = models
        self._changes = changes
        self._unit_of_work = unit_of_work
        self._access = access

    async def persist_initial(self, project: Project, dbml: str) -> DataModel:
        """Persist initial DBML nếu input và model vẫn không đổi."""
        async with self._unit_of_work:
            current_project = await self._access.require_owner(project.id)
            _ensure_analysis_unchanged(current_project, project)
            if await self._models.get_by_project_id(project.id):
                raise_model_exists()
            saved = await self._models.save(
                DataModel(
                    project_id=project.id,
                    dbml=dbml,
                    generated_from_requirement_revision=project.analyzed_requirement_revision,
                    generated_from_source_revision=project.analyzed_source_revision,
                )
            )
            await self._unit_of_work.commit()
        return saved

    async def persist_proposal(self, model: DataModel, project: Project, dbml: str) -> DataModelChange:
        """Upsert proposal sau khi kiểm tra context chưa đổi."""
        async with self._unit_of_work:
            current_project = await self._access.require_owner(model.project_id)
            _ensure_analysis_unchanged(current_project, project)
            current = await self._require_model(model.project_id)
            _ensure_revision(current.revision, model.revision)
            change = await self._upsert_change(current, dbml)
            await self._unit_of_work.commit()
        return change

    async def persist_regenerated(
        self,
        model: DataModel,
        project: Project,
        dbml: str,
    ) -> DataModel:
        """Ghi đè snapshot nếu analysis và model revision vẫn không đổi."""
        base_revision = model.revision
        async with self._unit_of_work:
            current_project = await self._access.require_owner(model.project_id)
            _ensure_analysis_unchanged(current_project, project)
            current = await self._require_model(model.project_id)
            _ensure_revision(current.revision, base_revision)
            current.update_dbml(dbml, base_revision)
            current.record_generation_revisions(
                project.analyzed_requirement_revision,
                project.analyzed_source_revision,
            )
            saved = await self._models.update_if_revision_matches(
                current,
                base_revision,
            )
            if saved is None:
                _raise_revision_conflict()
            await self._unit_of_work.commit()
        return saved

    async def _upsert_change(self, model: DataModel, dbml: str) -> DataModelChange:
        """Tạo mới hoặc thay active proposal của actor hiện tại."""
        actor_id = self._access.actor_id
        change = await self._changes.get_proposed_by_data_model_and_user(model.id, actor_id)
        if change is None:
            change = DataModelChange(
                data_model_id=model.id,
                user_id=actor_id,
                base_revision=model.revision,
                base_dbml=model.dbml,
                proposed_dbml=dbml,
            )
        else:
            change.replace_proposal(dbml, model)
        return await self._changes.save(change)

    async def _require_model(self, project_id: EntityID) -> DataModel:
        """Lấy Data Model hoặc báo not found."""
        model = await self._models.get_by_project_id(project_id)
        if model is None:
            raise BusinessException(ErrorCode.DATA_MODEL_NOT_FOUND, "Không tìm thấy Data Model.")
        return model


def _ensure_analysis_unchanged(current: Project, expected: Project) -> None:
    """Báo conflict khi input hoặc analysis đổi trong lúc Agent chạy."""
    revisions = (
        current.requirement_revision == expected.requirement_revision,
        current.source_revision == expected.source_revision,
        current.analyzed_requirement_revision == expected.analyzed_requirement_revision,
        current.analyzed_source_revision == expected.analyzed_source_revision,
    )
    if not all(revisions):
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Input đã đổi trong lúc Agent xử lý.")


def _ensure_revision(current: int, expected: int) -> None:
    """Báo conflict khi Data Model đổi trong lúc Agent chạy."""
    if current != expected:
        _raise_revision_conflict()


def _raise_revision_conflict() -> None:
    """Báo model đã thay đổi trong lúc Agent xử lý."""
    raise BusinessException(
        ErrorCode.DATA_MODEL_REVISION_CONFLICT,
        "Data Model đã thay đổi trong lúc Agent xử lý.",
    )


def raise_model_exists() -> None:
    """Báo conflict khi initial generation bị gọi lại."""
    raise BusinessException(
        ErrorCode.DATA_MODEL_ALREADY_EXISTS,
        "Data Model đã tồn tại; hãy dùng Update Data Model.",
    )
