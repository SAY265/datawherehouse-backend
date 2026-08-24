"""Quản lý dữ liệu nạp từ Frontend vào data_AI và lưu trữ sang data khi kết thúc phiên."""

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from config import get_settings
from src.common.logging import get_logger

logger = get_logger(__name__)


class SessionDataManager:
    """Quản lý vòng đời tệp tin giữa thư mục data_AI (tạm thời) và data (lưu trữ lâu dài)."""

    def __init__(self, data_dir: Path | None = None, data_ai_dir: Path | None = None) -> None:
        settings = get_settings()
        self._data_dir = data_dir or settings.data_path
        self._data_ai_dir = data_ai_dir or settings.data_ai_path
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Đảm bảo các thư mục data và data_AI luôn tồn tại."""
        for directory in (self._data_dir, self._data_ai_dir):
            if directory.exists() and directory.is_symlink():
                raise ValueError("Thư mục dữ liệu không được là symbolic link.")
            directory.mkdir(parents=True, exist_ok=True)

    def scoped(self, scope_id: str) -> "SessionDataManager":
        """Create an isolated manager rooted under a trusted user/session scope."""
        safe_scope = scope_id.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", safe_scope):
            raise ValueError("Phạm vi dữ liệu không hợp lệ.")
        return SessionDataManager(
            data_dir=self._data_dir / safe_scope,
            data_ai_dir=self._data_ai_dir / safe_scope,
        )

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def data_ai_dir(self) -> Path:
        return self._data_ai_dir

    def save_ai_file(self, filename: str, content: bytes | str) -> Path:
        """Lưu tệp tin nạp từ Frontend vào thư mục data_AI để AI phân tích."""
        self._ensure_directories()
        clean_name = Path(filename).name
        if not clean_name or clean_name in {".", ".."} or len(clean_name) > 255 or "\x00" in clean_name:
            raise ValueError("Tên tệp không hợp lệ.")
        target_path = self._data_ai_dir / clean_name

        if isinstance(content, str):
            target_path.write_text(content, encoding="utf-8")
        else:
            target_path.write_bytes(content)

        logger.info("Đã lưu dữ liệu nguồn vào data_AI: %s (%d bytes)", clean_name, target_path.stat().st_size)
        return target_path

    def save_source_tables_metadata(
        self,
        domain: str,
        source_tables: list[dict[str, Any]],
        business_description: str = "",
        is_masking_enabled: bool = True,
    ) -> Path:
        """Lưu snapshot metadata cấu trúc bảng nguồn vào data_AI."""
        self._ensure_directories()
        normalized_domain = unicodedata.normalize("NFKD", domain.strip())
        ascii_domain = "".join(
            character for character in normalized_domain if not unicodedata.combining(character)
        )
        domain_safe = re.sub(r"[^A-Za-z0-9_-]+", "_", ascii_domain).strip("._-").lower()
        domain_safe = domain_safe[:80] or "general"
        filename = f"{domain_safe}_source_schema.json"
        target_path = self._data_ai_dir / filename

        payload = {
            "domain": domain,
            "business_description": business_description,
            "is_masking_enabled": is_masking_enabled,
            "tables_count": len(source_tables),
            "tables": source_tables,
        }

        target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Đã lưu metadata cấu trúc nguồn vào data_AI: %s", filename)
        return target_path

    def list_ai_files(self) -> list[str]:
        """Liệt kê danh sách các tệp tin hiện có trong data_AI (bỏ qua .gitkeep)."""
        self._ensure_directories()
        return [
            f.name
            for f in self._data_ai_dir.iterdir()
            if f.is_file() and not f.is_symlink() and f.name != ".gitkeep"
        ]

    def list_data_files(self) -> list[str]:
        """Liệt kê danh sách các tệp tin trong thư mục data vĩnh viễn."""
        self._ensure_directories()
        return [
            f.name
            for f in self._data_dir.iterdir()
            if f.is_file() and not f.is_symlink() and f.name not in (".gitkeep", ".env.example")
        ]

    def read_ai_file(self, filename: str) -> bytes | None:
        """Đọc nội dung một tệp tin trong data_AI."""
        clean_name = Path(filename).name
        target_path = self._data_ai_dir / clean_name
        if target_path.exists() and target_path.is_file() and not target_path.is_symlink():
            return target_path.read_bytes()
        return None

    def get_ai_data_context(self) -> dict[str, Any]:
        """Đọc và tổng hợp toàn bộ dữ liệu nguồn từ data_AI để làm ngữ cảnh phân tích cho AI."""
        self._ensure_directories()
        ai_files = self.list_ai_files()
        context: dict[str, Any] = {
            "files_count": len(ai_files),
            "files": [],
            "schemas": [],
        }

        for filename in ai_files:
            file_path = self._data_ai_dir / filename
            file_info: dict[str, Any] = {
                "name": filename,
                "size_bytes": file_path.stat().st_size,
            }

            if filename.endswith(".json"):
                try:
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and "tables" in data:
                        context["schemas"].append(data)
                except Exception:
                    pass

            context["files"].append(file_info)

        return context

    def archive_and_clear_session(self, session_id: str | None = None) -> dict[str, Any]:
        """
        Kết thúc phiên:
        1. Quét tất cả file trong data_AI.
        2. Nếu file đã tồn tại trong data thì XÓA HẲN file cũ trong data.
        3. Di chuyển file từ data_AI vào data.
        4. Dọn sạch thư mục data_AI.
        """
        self._ensure_directories()
        archived_files: list[str] = []
        replaced_files: list[str] = []

        for item in self._data_ai_dir.iterdir():
            if not item.is_file() or item.is_symlink() or item.name == ".gitkeep":
                continue

            filename = item.name
            dest_path = self._data_dir / filename

            # Path.replace is atomic on the same filesystem and preserves the old
            # destination if moving the new file fails before replacement.
            if dest_path.exists():
                replaced_files.append(filename)

            # Di chuyển từ data_AI sang data
            try:
                item.replace(dest_path)
                archived_files.append(filename)
                logger.info("Đã chuyển tệp từ data_AI sang data: %s", filename)
            except Exception as exc:
                logger.error("Lỗi khi chuyển tệp %s sang data: %s", filename, exc)

        # Xóa dọn dẹp sạch toàn bộ file còn lại trong data_AI (nếu có)
        cleared_count = 0
        for remaining in self._data_ai_dir.iterdir():
            if remaining.is_file() and not remaining.is_symlink() and remaining.name != ".gitkeep":
                try:
                    remaining.unlink()
                    cleared_count += 1
                except Exception:
                    pass

        return {
            "status": "success",
            "session_id": session_id,
            "archived_files": archived_files,
            "replaced_files": replaced_files,
            "total_archived": len(archived_files),
            "cleared_from_data_ai": cleared_count,
            "message": f"Đã chuyển {len(archived_files)} file từ data_AI sang data và dọn sạch data_AI thành công.",
        }


_global_session_data_manager: SessionDataManager | None = None


def get_session_data_manager() -> SessionDataManager:
    """Singleton getter cho SessionDataManager."""
    global _global_session_data_manager
    if _global_session_data_manager is None:
        _global_session_data_manager = SessionDataManager()
    return _global_session_data_manager
