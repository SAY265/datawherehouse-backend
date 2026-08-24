"""Application service duy nhất cho module Data Model."""

from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.artifact_generator import IDataModelArtifactGenerator
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import (
    GetDataModelInput,
    RunRelationshipAgentInput,
    UpdateDataModelInput,
)
from src.application.data_models.insight_analyzer import IDataModelInsightAnalyzer
from src.application.data_models.output import (
    DataModelDdlOutput,
    DataModelInsightOutput,
    DataModelOutput,
    RelationshipAgentOutput,
    RelationshipRefOutput,
    RelationshipWarningOutput,
)
from src.application.projects.relationship_inferrer import run_relationship_agent
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


class DataModelService(IDataModelService):
    """Điều phối các use case của Data Model qua domain repository."""

    def __init__(
        self,
        repository: IDataModelRepository,
        unit_of_work: IUnitOfWork,
        artifact_generator: IDataModelArtifactGenerator | None = None,
        insight_analyzer: IDataModelInsightAnalyzer | None = None,
        access_guard: ProjectAccessGuard | None = None,
        current_user_id: EntityID | None = None,
    ) -> None:
        """Khởi tạo service với repository và transaction abstraction."""
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._artifact_generator = artifact_generator
        self._insight_analyzer = insight_analyzer
        self._access_guard = access_guard
        self._current_user_id = current_user_id

    @override
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy Data Model theo project và chuẩn hóa lỗi không tồn tại."""
        await self._authorize(data.project_id)
        data_model = await self._repository.get_by_project_id(data.project_id)
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        return DataModelOutput.from_domain(data_model)

    @override
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Cập nhật DBML dựa trên base revision."""
        await self._authorize(data.project_id)
        current = self._get_target(await self._repository.get_by_project_id(data.project_id), data)
        current.update_dbml(data.dbml, data.base_revision)
        updated = await self._repository.update_if_revision_matches(current, data.base_revision)
        if updated is None:
            raise BusinessException(
                code=ErrorCode.REVISION_CONFLICT,
                message="Data Model đã được cập nhật bởi một thao tác khác.",
            )
        await self._unit_of_work.commit()
        return DataModelOutput.from_domain(updated)

    @override
    async def generate_ddl(self, data: GetDataModelInput, dialect: str) -> DataModelDdlOutput:
        """Sinh DDL đúng revision từ DBML đang được lưu."""
        await self._authorize(data.project_id)
        current = self._require_current(await self._repository.get_by_project_id(data.project_id))
        return DataModelDdlOutput(
            ddl=self._require_artifact_generator().generate_ddl(current.dbml, dialect),
            dialect=dialect,
            revision=current.revision,
        )

    @override
    async def get_insights(self, data: GetDataModelInput) -> list[DataModelInsightOutput]:
        """Phân tích trực tiếp DBML hiện tại, không dùng dữ liệu demo frontend."""
        await self._authorize(data.project_id)
        current = self._require_current(await self._repository.get_by_project_id(data.project_id))
        if self._insight_analyzer is not None:
            return await self._insight_analyzer.analyze(current.dbml)
        return self._require_artifact_generator().analyze(current.dbml)

    @override
    async def run_relationship_agent(
        self, data: RunRelationshipAgentInput
    ) -> RelationshipAgentOutput:
        """Chạy bộ suy luận AI trên draft; không tự ghi DB để tránh conflict."""
        await self._authorize(data.project_id)
        from src.application.projects.relationship_inferrer import run_relationship_agent_with_ai

        result = await run_relationship_agent_with_ai(data.dbml)
        return RelationshipAgentOutput(
            dbml=result.dbml,
            added_relationships=[RelationshipRefOutput(**ref) for ref in result.added_refs],
            warnings=[
                RelationshipWarningOutput(
                    code=warning.code,
                    message=warning.message,
                    table_name=warning.table_name,
                    column_name=warning.column_name,
                    expected_table=warning.expected_table,
                )
                for warning in result.warnings
            ],
        )

    async def _authorize(self, project_id: EntityID) -> None:
        if self._access_guard is not None and self._current_user_id is not None:
            await self._access_guard.verify_project_access(project_id, self._current_user_id)

    def _require_artifact_generator(self) -> IDataModelArtifactGenerator:
        if self._artifact_generator is None:
            raise RuntimeError("Data Model artifact generator chưa được cấu hình.")
        return self._artifact_generator

    @staticmethod
    def _require_current(current: DataModel | None) -> DataModel:
        if current is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        return current

    @staticmethod
    def _get_target(current: DataModel | None, data: UpdateDataModelInput) -> DataModel:
        """Kiểm tra và trả Data Model đúng ID trong input."""
        if current is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        if current.id != data.data_model_id:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL,
                message="Data Model không thuộc dự án được yêu cầu.",
            )
        return current
