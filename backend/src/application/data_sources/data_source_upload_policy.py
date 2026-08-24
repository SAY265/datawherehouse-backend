"""Quy tắc batch upload dành cho Data Source application flow."""

from pathlib import Path
from typing import NoReturn

from src.application.data_sources.input import UploadDataSourcesInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_ALLOWED_FILES = 20
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = frozenset({
    ".csv", ".tsv", ".xls", ".xlsx", ".md", ".markdown", ".sql",
})


def validate_upload(
    data: UploadDataSourcesInput,
    existing_names: frozenset[str],
) -> None:
    """Kiểm tra batch và tổng source sau khi thay thế file trùng tên."""
    if not data.files:
        _raise(ErrorCode.FILE_EMPTY, "Danh sách file không được để trống.")
    final_names = existing_names | {item.filename.casefold() for item in data.files}
    if len(final_names) > MAX_ALLOWED_FILES:
        _raise(ErrorCode.MAX_FILES_EXCEEDED, f"Mỗi Project chỉ có tối đa {MAX_ALLOWED_FILES} file.")
    for item in data.files:
        if file_extension(item.filename) not in ALLOWED_EXTENSIONS:
            supported = ", ".join(sorted(ALLOWED_EXTENSIONS))
            _raise(ErrorCode.INVALID_FILE_FORMAT, f"Định dạng không được hỗ trợ. Cho phép: {supported}.")
        if len(item.content) > MAX_FILE_SIZE:
            size_mb = MAX_FILE_SIZE // (1024 * 1024)
            _raise(ErrorCode.FILE_TOO_LARGE, f"Mỗi file không được vượt quá {size_mb} MB.")


def file_extension(filename: str) -> str:
    """Trả extension chữ thường của tên file."""
    return Path(filename).suffix.lower()


def _raise(code: ErrorCode, message: str) -> NoReturn:
    raise BusinessException(code=code, message=message)
