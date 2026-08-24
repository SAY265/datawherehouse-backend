"""Sinh PostgreSQL DDL và insight cấu trúc bằng PyDBML."""

import re

try:
    from pydbml import PyDBML
except ImportError:
    PyDBML = None  # type: ignore

try:
    from sqlglot import transpile
except ImportError:
    transpile = None  # type: ignore
from src.application.data_models.artifact_generator import IDataModelArtifactGenerator
from src.application.data_models.output import DataModelInsightOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from typing_extensions import override


class PyDbmlArtifactGenerator(IDataModelArtifactGenerator):
    """Adapter PyDBML cho codegen và phân tích Data Model."""

    @override
    def generate_ddl(self, dbml: str, dialect: str) -> str:
        normalized = dialect.strip().lower()
        if normalized not in {"postgresql", "postgres"}:
            raise BusinessException(
                code=ErrorCode.UNSUPPORTED_DDL_DIALECT,
                message=f"Dialect '{dialect}' chưa được hỗ trợ.",
            )
        database = self._parse(dbml)
        statements = transpile(database.sql, read="sqlite", write="postgres")
        return ";\n\n".join(statements).strip() + ";"

    @override
    def analyze(self, dbml: str) -> list[DataModelInsightOutput]:
        database = self._parse(dbml)
        outgoing_refs: dict[str, list[str]] = {}
        incoming_refs: dict[str, list[str]] = {}
        outgoing_columns: dict[str, set[str]] = {}

        for ref in database.refs:
            if ref.col1 and ref.col2 and getattr(ref.col1[0], "table", None) and getattr(ref.col2[0], "table", None):
                src_tbl = ref.col1[0].table.name
                src_col = ref.col1[0].name
                tgt_tbl = ref.col2[0].table.name
                tgt_col = ref.col2[0].name
                outgoing_refs.setdefault(src_tbl, []).append(f"{src_tbl}.{src_col} > {tgt_tbl}.{tgt_col}")
                outgoing_columns.setdefault(src_tbl, set()).add(src_col)
                incoming_refs.setdefault(tgt_tbl, []).append(f"{tgt_tbl}.{tgt_col} < {src_tbl}.{src_col}")

        total_tables = len(database.tables)
        insights: list[DataModelInsightOutput] = []

        for table in database.tables:
            primary_keys = [column.name for column in table.columns if column.pk]
            if primary_keys:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:grain",
                        table_name=table.name,
                        severity="info",
                        title="Grain của bảng",
                        description=("Mỗi dòng được định danh bởi khóa " + ", ".join(primary_keys) + "."),
                    )
                )
            else:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:missing-primary-key",
                        table_name=table.name,
                        severity="error",
                        title="Thiếu khóa chính",
                        description="Bảng chưa có cột khóa chính để xác định grain ổn định.",
                    )
                )

            # 1. Phân tích Vai trò & Mục đích của bảng
            fk_like_columns = [
                column.name
                for column in table.columns
                if not column.pk
                and re.search(r"_(?:id|key|code|sk|pk|no|uuid|ref)$", column.name, re.IGNORECASE)
            ]
            unresolved_fk_columns = [
                column
                for column in fk_like_columns
                if column not in outgoing_columns.get(table.name, set())
            ]
            relationship_count = len(outgoing_refs.get(table.name, [])) + len(
                incoming_refs.get(table.name, [])
            )
            if (
                primary_keys
                and not unresolved_fk_columns
                and (total_tables == 1 or relationship_count > 0)
            ):
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:schema-complete",
                        table_name=table.name,
                        severity="info",
                        title="Bảng đã đầy đủ thông tin",
                        description=(
                            f"Đã xác định PK ({', '.join(primary_keys)}), {len(table.columns)} cột "
                            f"và {relationship_count} quan hệ hợp lệ; không còn khóa ngoại mồ côi."
                        ),
                    )
                )
            elif unresolved_fk_columns:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:unresolved-foreign-keys",
                        table_name=table.name,
                        severity="warn",
                        title="Khóa ngoại chưa được liên kết",
                        description=(
                            "Chưa tìm thấy bảng đích hợp lệ cho: "
                            + ", ".join(unresolved_fk_columns)
                            + ". Hãy bổ sung bảng đích hoặc chạy Relationship Agent."
                        ),
                    )
                )

            is_fact = table.name.lower().startswith("fact_") or len(outgoing_refs.get(table.name, [])) > 0
            is_dim = table.name.lower().startswith("dim_") or len(incoming_refs.get(table.name, [])) > 0

            if is_fact:
                role_desc = "Bảng đóng vai trò Fact/Transaction lưu trữ số liệu giao dịch, biến cố kinh doanh."
            elif is_dim:
                role_desc = "Bảng đóng vai trò Dimension/Danh mục cung cấp thuộc tính phân tích và ngữ cảnh lọc báo cáo."
            else:
                role_desc = "Bảng dữ liệu nguồn hoặc danh mục độc lập (Source / Master Entity)."

            insights.append(
                DataModelInsightOutput(
                    id=f"{table.name}:purpose",
                    table_name=table.name,
                    severity="info",
                    title="Mục đích & Vai trò bảng",
                    description=role_desc,
                )
            )

            # 2. Phân tích Lý do & Ý nghĩa các quan hệ (Ref)
            out_list = outgoing_refs.get(table.name, [])
            in_list = incoming_refs.get(table.name, [])
            if out_list or in_list:
                rel_parts = []
                if out_list:
                    rel_parts.append("Tham chiếu tới: " + ", ".join(out_list))
                if in_list:
                    rel_parts.append("Được tham chiếu bởi: " + ", ".join(in_list))
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:relationships",
                        table_name=table.name,
                        severity="info",
                        title="Lý do & Ý nghĩa liên kết",
                        description=" ".join(rel_parts) + ". Phục vụ kết hợp dữ liệu giữa các bảng mà không gây trùng lặp.",
                    )
                )

            # 3. Đánh giá tính cần thiết & Cảnh báo bảng / quan hệ thừa
            if table.name.lower().startswith("dim_") and len(table.columns) <= 2 and any(k in table.name.lower() for k in ("name", "desc", "val", "column")):
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:necessity-check",
                        table_name=table.name,
                        severity="warn",
                        title="Đánh giá tính cần thiết (Cảnh báo bảng giả định)",
                        description="Bảng có dấu hiệu là Dimension giả định tự động tạo. Khuyến nghị kiểm tra nếu có thể hợp nhất trực tiếp vào bảng chính hoặc loại bỏ.",
                    )
                )
            elif not out_list and not in_list and total_tables > 1:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:island-check",
                        table_name=table.name,
                        severity="info",
                        title="Đánh giá liên kết bảng",
                        description="Bảng hiện đang đứng độc lập (chưa có liên kết với bảng khác). Nếu đây là thực thể riêng biệt thì hoàn toàn hợp lệ.",
                    )
                )

            if not table.indexes and len(table.columns) >= 3:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:index-review",
                        table_name=table.name,
                        severity="warn",
                        title="Cần rà soát index",
                        description="Ngoài khóa chính, bảng chưa khai báo index phục vụ truy vấn.",
                    )
                )
        return insights

    @staticmethod
    def _parse(dbml: str):
        try:
            return PyDBML(dbml)
        except Exception as exc:
            raise BusinessException(
                code=ErrorCode.INVALID_DBML_CONTENT,
                message="Không thể sinh artifact từ DBML không hợp lệ.",
            ) from exc
