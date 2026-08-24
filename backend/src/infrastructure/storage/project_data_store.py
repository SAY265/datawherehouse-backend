"""Quản lý kho dữ liệu riêng biệt cho từng dự án trong backend/data."""

import json
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any

from config import get_settings
from src.common.logging import get_logger

logger = get_logger(__name__)


def slugify_project_name(name: str) -> str:
    """Chuẩn hóa tên dự án thành định dạng slug an toàn cho thư mục và tên file."""
    normalized = unicodedata.normalize("NFKD", name.strip())
    ascii_name = "".join(c for c in normalized if not unicodedata.combining(c))
    safe_slug = re.sub(r"[^A-Za-z0-9_-]+", "_", ascii_name).strip("._-").lower()
    return safe_slug[:60] or "du_an"


class ProjectDataStore:
    """Quản lý kho dữ liệu riêng biệt trên đĩa cho từng dự án trong thư mục backend/data."""

    def __init__(self, base_data_dir: Path | None = None) -> None:
        settings = get_settings()
        self._base_data_dir = base_data_dir or settings.data_path
        self._base_data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def base_data_dir(self) -> Path:
        return self._base_data_dir

    def get_project_dir_name(self, project_id: str, project_name: str = "") -> str:
        """Sinh tên thư mục chuẩn hóa cho dự án: <safe_name>_<short_id>."""
        short_id = str(project_id).replace("-", "")[:8]
        safe_name = slugify_project_name(project_name) if project_name else "project"
        return f"{safe_name}_{short_id}"

    def find_project_dir(self, project_id: str) -> Path | None:
        """Tìm thư mục kho dữ liệu của dự án theo project_id (hỗ trợ cả slug cũ và UUID)."""
        pid_str = str(project_id).strip()
        short_id = pid_str.replace("-", "")[:8]

        # 1. Kiểm tra thư mục khớp short_id ở đuôi hoặc tên thư mục chính là project_id
        if not self._base_data_dir.exists():
            return None

        for item in self._base_data_dir.iterdir():
            if item.is_dir() and not item.is_symlink():
                # Khớp project_id đầy đủ hoặc kết thúc bằng _<short_id>
                if item.name == pid_str or item.name.endswith(f"_{short_id}"):
                    return item

        return None

    def get_or_create_project_dir(self, project_id: str, project_name: str = "") -> Path:
        """Lấy thư mục kho hiện có hoặc tạo thư mục mới cho dự án."""
        existing = self.find_project_dir(project_id)
        if existing is not None:
            # Tạo thư mục sources nếu chưa có
            (existing / "sources").mkdir(parents=True, exist_ok=True)
            return existing

        dir_name = self.get_project_dir_name(project_id, project_name)
        project_dir = self._base_data_dir / dir_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "sources").mkdir(parents=True, exist_ok=True)
        (project_dir / "revisions").mkdir(parents=True, exist_ok=True)
        logger.info("Đã tạo kho dữ liệu riêng cho dự án %s tại: %s", project_id, project_dir)
        return project_dir

    def init_project_repository(
        self,
        project_id: str,
        project_name: str,
        domain: str = "general",
        target_dialect: str = "postgresql",
        business_description: str = "",
        requirement: str = "",
        status: str = "ACTIVE",
        source_tables: list[dict[str, Any]] | None = None,
        initial_dbml: str = "",
    ) -> Path:
        """Khởi tạo toàn bộ kho tệp cho dự án mới được tạo từ input của người dùng."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)

        # 1. Ghi file project_meta.json
        meta_payload = {
            "project_id": str(project_id),
            "name": project_name,
            "domain": domain,
            "target_dialect": target_dialect,
            "business_description": business_description,
            "requirement": requirement,
            "status": status,
        }
        meta_path = project_dir / "project_meta.json"
        meta_path.write_text(json.dumps(meta_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. Ghi file source_tables.json
        tables = source_tables or []
        tables_path = project_dir / "source_tables.json"
        tables_path.write_text(
            json.dumps(
                {
                    "project_id": str(project_id),
                    "domain": domain,
                    "tables_count": len(tables),
                    "tables": tables,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        # 3. Ghi file model.dbml nếu có
        if initial_dbml:
            dbml_path = project_dir / "model.dbml"
            dbml_path.write_text(initial_dbml, encoding="utf-8")

        logger.info("Đã khởi tạo metadata và tệp kho cho dự án: %s", project_name)
        return project_dir

    def save_source_file(
        self,
        project_id: str,
        filename: str,
        content: bytes | str,
        project_name: str = "",
    ) -> Path:
        """Lưu một tệp dữ liệu nguồn (Excel, CSV, SQL, Markdown) vào thư mục sources của dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        sources_dir = project_dir / "sources"
        sources_dir.mkdir(parents=True, exist_ok=True)

        clean_name = Path(filename).name
        if not clean_name or clean_name in {".", ".."} or len(clean_name) > 255:
            raise ValueError("Tên tệp tin nguồn không hợp lệ.")

        target_path = sources_dir / clean_name
        if isinstance(content, str):
            target_path.write_text(content, encoding="utf-8")
        else:
            target_path.write_bytes(content)

        logger.info(
            "Đã lưu file nguồn %s (%d bytes) vào kho dự án %s",
            clean_name,
            target_path.stat().st_size,
            project_id,
        )
        return target_path

    def update_project_meta(
        self,
        project_id: str,
        updates: dict[str, Any],
        project_name: str = "",
    ) -> Path:
        """Cập nhật thông tin trong project_meta.json của kho dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        meta_path = project_dir / "project_meta.json"

        current_meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                current_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                current_meta = {}

        current_meta.update(updates)
        current_meta["project_id"] = str(project_id)
        meta_path.write_text(json.dumps(current_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        # Đổi tên thư mục kho nếu tên dự án thay đổi
        new_name = updates.get("name")
        if new_name and slugify_project_name(new_name) != slugify_project_name(current_meta.get("name", "")):
            new_dir_name = self.get_project_dir_name(project_id, new_name)
            new_project_dir = self._base_data_dir / new_dir_name
            if not new_project_dir.exists():
                try:
                    project_dir.rename(new_project_dir)
                    project_dir = new_project_dir
                except Exception as exc:
                    logger.warning("Không thể đổi tên thư mục kho: %s", exc)

        return meta_path

    def save_source_tables(
        self,
        project_id: str,
        source_tables: list[dict[str, Any]],
        domain: str = "general",
        project_name: str = "",
    ) -> Path:
        """Lưu danh sách cấu trúc bảng nguồn vào kho dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        tables_path = project_dir / "source_tables.json"
        payload = {
            "project_id": str(project_id),
            "domain": domain,
            "tables_count": len(source_tables),
            "tables": source_tables,
        }
        tables_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return tables_path

    def save_dbml_model(
        self,
        project_id: str,
        dbml_code: str,
        revision: int = 1,
        project_name: str = "",
    ) -> Path:
        """Ghi mã DBML hiện tại và lưu snapshot revision vào kho của dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        dbml_path = project_dir / "model.dbml"
        dbml_path.write_text(dbml_code, encoding="utf-8")

        # Lưu bản snapshot revision
        revisions_dir = project_dir / "revisions"
        revisions_dir.mkdir(parents=True, exist_ok=True)
        rev_path = revisions_dir / f"rev_{revision}.dbml"
        rev_path.write_text(dbml_code, encoding="utf-8")

        logger.info("Đã lưu mã DBML (revision %d) vào kho dự án %s", revision, project_id)
        return dbml_path

    def save_ddl_sql(
        self,
        project_id: str,
        ddl_code: str,
        project_name: str = "",
    ) -> Path:
        """Lưu mã DDL SQL đã sinh hoặc chỉnh sửa vào kho của dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        ddl_path = project_dir / "schema.sql"
        ddl_path.write_text(ddl_code, encoding="utf-8")
        logger.info("Đã lưu mã DDL schema.sql vào kho dự án %s", project_id)
        return ddl_path

    def save_sandbox_config(
        self,
        project_id: str,
        config: dict[str, Any],
        project_name: str = "",
    ) -> Path:
        """Lưu cấu hình sandbox vào kho của dự án."""
        project_dir = self.get_or_create_project_dir(project_id, project_name)
        cfg_path = project_dir / "sandbox_config.json"
        cfg_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        return cfg_path

    def get_project_storage_summary(self, project_id: str) -> dict[str, Any]:
        """Lấy thông tin tổng quan về các tệp tin trong kho dữ liệu của dự án."""
        project_dir = self.find_project_dir(project_id)
        if project_dir is None or not project_dir.exists():
            return {
                "exists": False,
                "project_id": str(project_id),
                "directory_name": "",
                "total_files": 0,
                "source_files": [],
                "has_meta": False,
                "has_source_tables": False,
                "has_dbml": False,
                "has_ddl": False,
                "has_sandbox_config": False,
            }

        sources_dir = project_dir / "sources"
        source_files = (
            [
                {"name": f.name, "size_bytes": f.stat().st_size}
                for f in sources_dir.iterdir()
                if f.is_file() and not f.is_symlink()
            ]
            if sources_dir.exists()
            else []
        )

        return {
            "exists": True,
            "project_id": str(project_id),
            "directory_name": project_dir.name,
            "directory_path": str(project_dir),
            "total_files": len(list(project_dir.rglob("*"))),
            "source_files": source_files,
            "has_meta": (project_dir / "project_meta.json").exists(),
            "has_source_tables": (project_dir / "source_tables.json").exists(),
            "has_dbml": (project_dir / "model.dbml").exists(),
            "has_ddl": (project_dir / "schema.sql").exists(),
            "has_sandbox_config": (project_dir / "sandbox_config.json").exists(),
        }

    def delete_project_repository(self, project_id: str) -> bool:
        """Xóa toàn bộ thư mục kho dữ liệu của dự án khi dự án bị xóa."""
        project_dir = self.find_project_dir(project_id)
        if project_dir is not None and project_dir.exists():
            try:
                shutil.rmtree(project_dir)
                logger.info("Đã xóa kho dữ liệu của dự án: %s (%s)", project_id, project_dir)
                return True
            except Exception as exc:
                logger.error("Lỗi khi xóa kho dữ liệu dự án %s: %s", project_id, exc)
                return False
        return False


_global_project_data_store: ProjectDataStore | None = None


def get_project_data_store() -> ProjectDataStore:
    """Singleton getter cho ProjectDataStore."""
    global _global_project_data_store
    if _global_project_data_store is None:
        _global_project_data_store = ProjectDataStore()
    return _global_project_data_store
