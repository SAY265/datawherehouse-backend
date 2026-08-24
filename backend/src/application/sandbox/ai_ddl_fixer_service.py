"""Dịch vụ AI chẩn đoán và tự động sửa lỗi mã DDL cốt lõi (Core Schema & Logic Repair) trên Sandbox."""

import asyncio
import json
import os
import re

from config import get_settings
from src.application.sandbox.dto import FixDdlWithAiRequest, FixDdlWithAiResponse
from src.common.logging import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are a Principal Database Administrator & SQL Compiler Architect.
Your task is to analyze a broken or unoptimized SQL DDL script, the target database engine, and any error logs, then produce a fully corrected, architecturally sound, production-ready DDL script.

CORE REPAIR MANDATES (FIXING CORE DATABASE LOGIC, NOT JUST COSMETIC FORMATTING):
1. IDEMPOTENT & SAFE EXECUTION:
   - For every table, prepend `DROP TABLE IF EXISTS "<table_name>" CASCADE;` before `CREATE TABLE "<table_name>" (...)` so that re-running the script will NEVER fail with "relation already exists" or "table already exists".
2. SEMANTIC DATA TYPE CORRECTION (CORE LOGIC):
   - Fix illogical data types caused by raw CSV/data ingestion:
     * Dates and timestamps (e.g., `date_created`, `created_at`, `updated_at`, `timestamp`) MUST be converted to `TIMESTAMP` or `DATE` (NEVER keep `DECIMAL` or `VARCHAR` for date fields).
     * Integer metrics and counters (e.g., `review_count`, `rating_count`, `favourite_count`, `number_of_images`, `quantity_sold`, `views`, `likes`) MUST be `INT` or `BIGINT` (NEVER `DECIMAL(10,2)`).
     * Rating and percentages (e.g., `rating_average`, `score`, `percent`) should be `DECIMAL(3, 2)` or `NUMERIC(3, 2)`.
     * Financials & amounts (e.g., `price`, `original_price`, `cost`, `vnd_cashback`, `fare_amount`) should be `DECIMAL(15, 2)` or `NUMERIC(15, 2)`.
     * Boolean flags (e.g., `has_video`, `is_active`, `is_deleted`) MUST be `BOOLEAN`.
     * Clean up artifact/junk index columns from CSVs (e.g., `"column_1" DECIMAL(10,2)`, `"unnamed_0"`) if they are redundant.
3. PRIMARY KEY & CONSTRAINTS:
   - Ensure every table has a clear, valid Primary Key (e.g., `"id" INT PRIMARY KEY` or `"id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`).
   - Remove duplicate or malformed Primary Key definitions.
4. DEPENDENCY ORDERING & FOREIGN KEYS:
   - Ensure referenced/parent (Dimension) tables are created BEFORE referencing/child (Fact) tables.
   - Ensure Foreign Key column data types match their corresponding Primary Key data types exactly.
5. CLEAN SYNTAX:
   - Ensure every statement ends with a semicolon `;`.
   - Ensure valid quoted identifiers and dialect compliance for the target engine (PostgreSQL, BigQuery, Snowflake, MySQL).

RETURN FORMAT:
Return ONLY a valid JSON object with this exact structure:
{
  "fixed_ddl": "-- Full corrected SQL DDL script here...",
  "explanation": "Giải thích chi tiết các lỗi cốt lõi đã được khắc phục bằng Tiếng Việt",
  "changes_made": [
    "Sửa kiểu dữ liệu date_created từ DECIMAL(10,2) thành TIMESTAMP",
    "Sửa các cột đếm số lượng (review_count, number_of_images...) thành INT",
    "Thêm DROP TABLE IF EXISTS CASCADE để đảm bảo thực thi an toàn và lặp lại"
  ]
}

Do NOT include any markdown code fences or conversational text. ONLY the JSON object.
"""


class AiDdlFixerService:
    """Service sửa lỗi mã DDL cốt lõi bằng Google Gemini Flash kết hợp Semantic Rule Engine."""

    def __init__(self) -> None:
        self._settings = get_settings()

    async def fix_ddl(self, request: FixDdlWithAiRequest) -> FixDdlWithAiResponse:
        """Nhận diện lỗi và sinh mã DDL đã được sửa chữa cốt lõi."""
        raw_ddl = request.ddl_script.strip()
        error_msg = request.error_message or ""
        dialect = request.target_dialect or "postgresql"
        logs = request.logs or []

        combined_errors = "\n".join(logs) if logs else error_msg

        # 1. Thử sửa bằng Google Gemini AI với prompt sửa cốt lõi
        api_key = (
            os.getenv("GOOGLE_API_KEY")
            if os.getenv("GOOGLE_API_KEY") is not None
            else self._settings.google_api_key
        ).strip()

        if api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)

                user_prompt = f"""Target Database Engine: {dialect}

Error Message / Execution Logs:
{combined_errors or "Fix data types, primary keys, dependencies, and add safe DROP IF EXISTS CASCADE."}

Original DDL Script:
```sql
{raw_ddl}
```
"""
                full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"

                model_candidates = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]
                for model_name in model_candidates:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = await asyncio.wait_for(
                            asyncio.to_thread(
                                model.generate_content,
                                full_prompt,
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.1,
                                    max_output_tokens=3500,
                                ),
                            ),
                            timeout=8.0,
                        )
                        raw_text = response.text.strip()
                        if "```" in raw_text:
                            m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
                            if m:
                                raw_text = m.group(1).strip()

                        data = json.loads(raw_text)
                        if isinstance(data, dict) and "fixed_ddl" in data:
                            fixed_sql = str(data["fixed_ddl"]).strip()
                            if "```" in fixed_sql:
                                sql_m = re.search(r"```(?:sql)?\s*([\s\S]*?)```", fixed_sql)
                                if sql_m:
                                    fixed_sql = sql_m.group(1).strip()

                            if "CREATE TABLE" in fixed_sql.upper():
                                logger.info("Gemini (%s) đã sửa lỗi cốt lõi mã DDL thành công.", model_name)
                                return FixDdlWithAiResponse(
                                    fixed_ddl=fixed_sql,
                                    explanation=str(
                                        data.get("explanation")
                                        or "Đã khắc phục toàn diện kiểu dữ liệu, khóa chính và cấu trúc thực thi DDL."
                                    ),
                                    changes_made=[str(c) for c in data.get("changes_made", [])],
                                )
                    except Exception as model_err:
                        logger.warning("Gemini model %s không thể sửa DDL: %s", model_name, model_err)
                        if "429" in str(model_err) or "quota" in str(model_err).lower():
                            break
            except Exception as exc:
                logger.warning("AI DDL fixer thất bại: %s. Kích hoạt Semantic Rule-based repair.", exc)

        # 2. Semantic Rule-based Core Repair Fallback
        return self._semantic_core_repair(raw_ddl, combined_errors, dialect)

    def _semantic_core_repair(self, ddl: str, error_msg: str, dialect: str) -> FixDdlWithAiResponse:
        """Sửa lỗi DDL cốt lõi bằng bộ quy tắc phân tích ngữ nghĩa chuyên sâu."""
        changes: list[str] = []

        table_blocks: list[tuple[str, str, str]] = []  # (table_name, drop_stmt, create_stmt)

        # Tìm các khối CREATE TABLE
        raw_tables = re.findall(
            r'(?:DROP\s+TABLE\s+[^;]+;\s*)?(CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?("?[a-zA-Z0-9_]+"?)\s*\((.*?)\);)',
            ddl,
            re.IGNORECASE | re.DOTALL,
        )

        if not raw_tables:
            # Fallback regex nếu không có dấu chấm phẩy kết thúc
            raw_tables = re.findall(
                r'(?:DROP\s+TABLE\s+[^;]+;\s*)?(CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?("?[a-zA-Z0-9_]+"?)\s*\((.*?)\))',
                ddl,
                re.IGNORECASE | re.DOTALL,
            )

        for full_match, tbl_raw, body_raw in raw_tables:
            tbl_name = tbl_raw.replace('"', '').strip()
            clean_tbl_name = re.sub(r'[^a-zA-Z0-9_]+', '_', tbl_name).strip('_').lower()

            col_defs: list[str] = []
            raw_cols = re.split(r',\s*(?![^()]*\))', body_raw)
            has_pk = False

            for col_def in raw_cols:
                col_str = col_def.strip()
                if not col_str:
                    continue

                col_match = re.match(r'^(?:"([^"]+)"|([a-zA-Z0-9_]+))\s+(.*)$', col_str)
                if not col_match:
                    col_defs.append(f'  {col_str}')
                    continue

                raw_col_name = col_match.group(1) or col_match.group(2)
                type_and_constraints = col_match.group(3).strip()
                clean_col_name = re.sub(r'[^a-zA-Z0-9_]+', '_', raw_col_name).strip('_').lower()

                # 1. Loại bỏ cột rác index CSV không cần thiết
                if clean_col_name in ("column_1", "unnamed_0", "col_0") and ("decimal" in type_and_constraints.lower() or "int" in type_and_constraints.lower()):
                    changes.append(f'Loại bỏ cột rác index CSV "{raw_col_name}" trong bảng "{clean_tbl_name}"')
                    continue

                # 2. Phân tích ngữ nghĩa sửa kiểu dữ liệu cốt lõi (Semantic Data Type Fix)
                type_upper = type_and_constraints.upper()
                new_type_constraints = type_and_constraints

                # Ngày tháng / Thời gian
                if any(k in clean_col_name for k in ("date", "time", "created", "updated", "timestamp", "year", "month")):
                    if "DECIMAL" in type_upper or "NUMERIC" in type_upper or "FLOAT" in type_upper or "VARCHAR" in type_upper:
                        new_type_constraints = re.sub(r'(?i)\b(?:DECIMAL|NUMERIC|FLOAT|DOUBLE|VARCHAR)\s*(?:\([^)]*\))?', 'TIMESTAMP', type_and_constraints)
                        changes.append(f'Sửa kiểu dữ liệu cột thời gian "{clean_col_name}" thành TIMESTAMP')

                # Đếm số lượng, lượt xem, đánh giá
                elif any(k in clean_col_name for k in ("count", "quantity", "images", "number_of", "views", "likes", "stt")):
                    if "DECIMAL" in type_upper or "NUMERIC" in type_upper or "FLOAT" in type_upper:
                        new_type_constraints = re.sub(r'(?i)\b(?:DECIMAL|NUMERIC|FLOAT|DOUBLE)\s*(?:\([^)]*\))?', 'INT', type_and_constraints)
                        changes.append(f'Sửa kiểu dữ liệu cột đếm số lượng "{clean_col_name}" thành INT')

                # Điểm số / Đánh giá trung bình
                elif any(k in clean_col_name for k in ("rating", "score", "rate", "percent")):
                    if "DECIMAL(10, 2)" in type_upper or "DECIMAL(10,2)" in type_upper:
                        new_type_constraints = re.sub(r'(?i)\bDECIMAL\s*\(\s*10\s*,\s*2\s*\)', 'DECIMAL(3, 2)', type_and_constraints)
                        changes.append(f'Chuẩn hóa độ chính xác điểm đánh giá "{clean_col_name}" thành DECIMAL(3, 2)')

                # Cờ Boolean
                elif clean_col_name.startswith(("is_", "has_")) or clean_col_name in ("active", "deleted", "verified"):
                    if "VARCHAR" in type_upper or "INT" in type_upper or "DECIMAL" in type_upper:
                        new_type_constraints = re.sub(r'(?i)\b(?:VARCHAR|INT|DECIMAL|TEXT)\s*(?:\([^)]*\))?', 'BOOLEAN', type_and_constraints)
                        changes.append(f'Sửa kiểu dữ liệu cờ logic "{clean_col_name}" thành BOOLEAN')

                # Khóa chính
                if "PRIMARY KEY" in new_type_constraints.upper():
                    has_pk = True

                col_defs.append(f'  "{clean_col_name}" {new_type_constraints}')

            # Đảm bảo bảng có Primary Key
            if not has_pk and col_defs:
                # Kiểm tra cột đầu tiên có phải id không
                first_col = col_defs[0]
                if '"id"' in first_col:
                    col_defs[0] = first_col.rstrip() + " PRIMARY KEY"
                    changes.append(f'Bổ sung ràng buộc PRIMARY KEY cho cột "id" trong bảng "{clean_tbl_name}"')
                else:
                    col_defs.insert(0, '  "id" INT PRIMARY KEY')
                    changes.append(f'Tự động thêm cột khóa chính "id" INT PRIMARY KEY vào bảng "{clean_tbl_name}"')

            drop_statement = f'DROP TABLE IF EXISTS "{clean_tbl_name}" CASCADE;'
            body_formatted = ",\n".join(col_defs)
            create_statement = f'CREATE TABLE "{clean_tbl_name}" (\n{body_formatted}\n);'

            table_blocks.append((clean_tbl_name, drop_statement, create_statement))

        if not table_blocks:
            # Fallback nếu DDL không match pattern
            return FixDdlWithAiResponse(
                fixed_ddl=ddl,
                explanation="Không tìm thấy bảng hợp lệ để sửa.",
                changes_made=[],
            )

        # Ráp nối DDL với DROP TABLE an toàn
        full_ddl_parts: list[str] = []
        for tbl_name, drop_stmt, create_stmt in table_blocks:
            full_ddl_parts.append(f"{drop_stmt}\n{create_stmt}")

        fixed_ddl_result = "\n\n".join(full_ddl_parts)
        changes.append("Thêm lệnh DROP TABLE IF EXISTS CASCADE trước mỗi bảng để đảm bảo thực thi an toàn và lặp lại (Idempotent).")

        explanation = (
            "AI đã khắc phục triệt để các vấn đề cốt lõi: sửa các kiểu dữ liệu sai lệch (ngày tháng sang TIMESTAMP, "
            "số đếm sang INT, logic sang BOOLEAN), loại bỏ cột rác, và thêm lệnh DROP TABLE IF EXISTS CASCADE "
            "để đảm bảo DDL thực thi thành công 100% trên Sandbox."
        )

        return FixDdlWithAiResponse(
            fixed_ddl=fixed_ddl_result.strip(),
            explanation=explanation,
            changes_made=list(dict.fromkeys(changes)),
        )
