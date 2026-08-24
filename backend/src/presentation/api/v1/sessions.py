"""Authenticated, user-isolated session file lifecycle endpoints."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.security.pii_masking import mask_uploaded_file
from src.infrastructure.storage.session_data_manager import get_session_data_manager
from src.presentation.dependencies.auth import CurrentUserDependency, get_current_user
from src.presentation.routing import ApiResponseRoute

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = frozenset({".csv", ".tsv", ".xlsx", ".md", ".sql"})

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    route_class=ApiResponseRoute,
    dependencies=[Depends(get_current_user)],
)


class EndSessionRequest(BaseModel):
    """Payload yêu cầu kết thúc phiên."""

    session_id: str | None = Field(default=None, description="Mã định danh phiên làm việc")
    project_id: str | None = Field(default=None, description="Mã dự án nếu có")


class EndSessionResponse(BaseModel):
    """Kết quả giải phóng và lưu trữ dữ liệu phiên."""

    status: str
    session_id: str | None = None
    archived_files: list[str] = Field(default_factory=list)
    replaced_files: list[str] = Field(default_factory=list)
    total_archived: int = 0
    cleared_from_data_ai: int = 0
    message: str


class DataAiFilesResponse(BaseModel):
    """Danh sách tệp tin đang nằm trong thư mục data_AI."""

    files: list[str] = Field(default_factory=list)
    count: int = 0


class UploadDataResponse(BaseModel):
    """Kết quả nạp tệp tin vào data_AI."""

    filename: str
    size_bytes: int
    saved_to: str
    masking_applied: bool = False
    masked_columns: list[str] = Field(default_factory=list)
    message: str


@router.post("/end", response_model=EndSessionResponse, operation_id="endSession")
async def end_session(
    current_user: CurrentUserDependency,
    request: EndSessionRequest | None = None,
) -> EndSessionResponse:
    """
    Kết thúc phiên làm việc:
    - Quét toàn bộ tệp tin trong data_AI.
    - Nếu tệp tin đã tồn tại trong data thì XÓA HẲN tệp tin cũ trong data.
    - Lưu trữ / di chuyển toàn bộ tệp tin từ data_AI sang data.
    - Giải phóng và xóa sạch dữ liệu trong data_AI.
    """
    manager = get_session_data_manager().scoped(str(current_user.id))
    session_id = request.session_id if request else None
    result = manager.archive_and_clear_session(session_id=session_id)
    return EndSessionResponse(**result)


@router.get("/data-ai", response_model=DataAiFilesResponse, operation_id="listDataAiFiles")
async def list_data_ai_files(current_user: CurrentUserDependency) -> DataAiFilesResponse:
    """Liệt kê danh sách các tệp tin hiện đang được AI xử lý trong data_AI."""
    manager = get_session_data_manager().scoped(str(current_user.id))
    files = manager.list_ai_files()
    return DataAiFilesResponse(files=files, count=len(files))


@router.post("/upload", response_model=UploadDataResponse, operation_id="uploadToDataAi")
async def upload_file_to_data_ai(
    current_user: CurrentUserDependency,
    file: UploadFile = File(...),
    is_masking_enabled: Any = Form(default=True),
) -> UploadDataResponse:
    """Nạp tệp tin dữ liệu nguồn từ Frontend trực tiếp vào data_AI để AI phân tích."""
    manager = get_session_data_manager().scoped(str(current_user.id))
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    filename = file.filename or "uploaded_data.bin"
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise BusinessException(
            code=ErrorCode.VALIDATION_ERROR,
            message="Định dạng tệp không được hỗ trợ.",
        )
    if len(content) > MAX_UPLOAD_BYTES:
        raise BusinessException(
            code=ErrorCode.VALIDATION_ERROR,
            message="Tệp tải lên vượt quá giới hạn 25 MB.",
        )
    masking_active = (
        str(is_masking_enabled).lower() in ("true", "1", "yes")
        if isinstance(is_masking_enabled, str)
        else bool(is_masking_enabled)
    )
    masked_columns: list[str] = []
    if masking_active:
        try:
            masked_file = mask_uploaded_file(filename, content)
        except ValueError as exc:
            raise BusinessException(
                code=ErrorCode.VALIDATION_ERROR,
                message=str(exc),
            ) from exc
        content = masked_file.content
        masked_columns = list(masked_file.masked_columns)
    saved_path = manager.save_ai_file(filename=filename, content=content)

    return UploadDataResponse(
        filename=filename,
        size_bytes=len(content),
        saved_to=str(saved_path.name),
        masking_applied=masking_active,
        masked_columns=masked_columns,
        message="Đã nạp tệp vào vùng phân tích an toàn.",
    )
