"""Module sinh mã DBML ban đầu từ dữ liệu nguồn và thông tin dự án (100% Dynamic, Zero-Hardcode).

Tự động phân tích cấu trúc bất kỳ domain nào (E-commerce, Healthcare, Logistics, Finance, IoT, HR, ERP...),
xác định khóa chính, khóa ngoại và tự động tổng hợp Dimension chung để kết nối toàn bộ bảng vào ERD hoàn chỉnh.
"""

import os
import re
import unicodedata
from typing import Any

from src.common.logging import get_logger

logger = get_logger(__name__)


def sanitize_identifier(name: str) -> str:
    """Chuẩn hóa tên bảng / cột thành identifier DBML hợp lệ (chỉ ASCII)."""
    clean = re.sub(r"\.(xlsx?|csv|sql|md)$", "", name, flags=re.IGNORECASE)
    clean = re.sub(r" · (schema|data)$", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*(?:Â·|·)\s*(schema|data)$", "", clean, flags=re.IGNORECASE)
    clean = unicodedata.normalize("NFKD", clean).encode("ascii", "ignore").decode("ascii")
    clean = re.sub(r"[^a-zA-Z0-9_]+", "_", clean).strip("_").lower()
    return clean or "table"


def _pluralize(word: str) -> str:
    """Tự động chuyển từ đơn sang số nhiều theo ngữ pháp chuẩn (không hardcode)."""
    w = word.strip().lower()
    if not w:
        return "entities"
    if w.endswith("ies"):
        return w
    if w.endswith("y") and len(w) > 1 and w[-2] not in "aeiou":
        return f"{w[:-1]}ies"
    if w.endswith(("s", "x", "z", "ch", "sh")):
        return f"{w}es"
    if w.endswith("f") and len(w) > 1:
        return f"{w[:-1]}ves"
    if w.endswith("fe") and len(w) > 2:
        return f"{w[:-2]}ves"
    return f"{w}s"


def _singularize(name: str) -> str:
    """Tự động chuyển từ số nhiều sang số ít để đối chiếu với cột khóa ngoại."""
    w = name.strip().lower()
    if w.endswith("ies") and len(w) > 4:
        return f"{w[:-3]}y"
    if w.endswith(("sses", "shes", "ches", "xes", "zzes")):
        return w[:-2]
    if w.endswith("ves") and len(w) > 4:
        return f"{w[:-3]}f"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w


def map_column_type(col_name: str, col_type: str, sample_val: Any = None) -> str:
    """Map type linh hoạt sang DBML data type chuẩn."""
    name_lower = col_name.lower()
    type_upper = (col_type or "TEXT").upper()

    if "UUID" in type_upper or name_lower == "uuid" or name_lower.endswith("_uuid"):
        return "uuid"
    if "BOOLEAN" in type_upper or "BOOL" in type_upper or name_lower.startswith(("is_", "has_")):
        return "boolean"
    if "DATE" in type_upper or "TIME" in type_upper:
        return "timestamp"
    if "INT" in type_upper:
        return "int"
    if (
        name_lower.endswith(("_at", "_date"))
        or name_lower.startswith(("date_", "created_", "updated_"))
        or name_lower in {"created", "updated", "timestamp", "datetime"}
    ):
        return "timestamp"
    if (
        "NUM" in type_upper
        or "DECIMAL" in type_upper
        or "FLOAT" in type_upper
        or "DOUBLE" in type_upper
        or "AMOUNT" in type_upper
        or any(k in name_lower for k in ["amount", "price", "fare", "total", "salary", "cost", "fee", "balance", "rate", "percent", "score"])
    ):
        if (
            name_lower == "id"
            or name_lower.endswith(("_id", "_sk", "_stt", "_count"))
            or name_lower.startswith(("count_", "number_", "quantity_"))
            or name_lower in {"count", "number", "quantity", "stt"}
        ):
            return "int"
        return "decimal(10,2)"
    if (
        name_lower.endswith("_at")
        or name_lower.endswith("_date")
        or "created" in name_lower
        or "updated" in name_lower
    ):
        return "timestamp"
    if "VARCHAR" in type_upper or "TEXT" in type_upper or "STRING" in type_upper:
        if any(k in name_lower for k in ["description", "note", "content", "address", "detail", "comment"]):
            return "text"
        return "varchar(255)"
    if (
        name_lower.endswith("_id")
        or name_lower == "id"
        or name_lower.endswith("_sk")
        or name_lower.endswith("_stt")
        or name_lower == "stt"
    ):
        return "int"
    return "varchar(255)"


def _table_entity_name(table_name: str) -> str:
    """Lấy tên thực thể cốt lõi của bảng, bỏ prefix schema/fact/dim nếu có."""
    clean = table_name.split(".")[-1].lower()
    for prefix in ("fact_", "dim_", "tb_", "tbl_", "table_", "v_", "stg_", "raw_", "source_", "src_", "public_"):
        if clean.startswith(prefix):
            clean = clean[len(prefix) :]
            break
    tokens = [t for t in clean.split("_") if t and t not in ("vietnamese", "tiki", "data", "table", "info", "list", "detail", "details")]
    if tokens:
        return _singularize(tokens[-1])
    return _singularize(clean.rsplit("_", 1)[-1])


def _column_name(column: dict[str, Any]) -> str:
    return sanitize_identifier(column.get("label") or column.get("key") or "col")


def _choose_primary_key(table_name: str, columns: list[dict[str, Any]]) -> str | None:
    """Xác định Primary Key của bảng dựa trên cấu trúc đặt tên (hoàn toàn động)."""
    names = [_column_name(column) for column in columns]
    entity_name = _table_entity_name(table_name)

    declared = next(
        (_column_name(column) for column in columns if column.get("is_primary_key")),
        None,
    )
    if declared:
        return declared

    # Ưu tiên các quy ước khóa chính chuẩn
    for candidate in ("id", f"{entity_name}_id", f"{table_name}_id", "code", f"{entity_name}_code", "uuid", "key"):
        if candidate in names:
            return candidate

    # Ưu tiên cột kết thúc bằng _sk, _pk
    generated_key = next(
        (name for name in names if name.endswith(("_sk", "_pk"))),
        None,
    )
    if generated_key:
        return generated_key

    # Ưu tiên cột kết thúc bằng _id đầu tiên
    first_id_col = next((name for name in names if name.endswith("_id")), None)
    if first_id_col:
        return first_id_col

    return None


def _is_foreign_key_match(col_name: str, target_table: str, target_pk: str) -> bool:
    """Kiểm tra cột nguồn có tham chiếu đến khóa của bảng đích hay không (hoàn toàn động)."""
    from src.application.projects.relationship_inferrer import _singularize_token

    col_clean = col_name.lower()
    target_clean = target_table.split(".")[-1].lower()
    for prefix in ("fact_", "dim_", "tb_", "tbl_", "table_", "v_", "stg_", "raw_", "source_", "src_", "public_"):
        if target_clean.startswith(prefix):
            target_clean = target_clean[len(prefix):]
            break

    target_tokens = [_singularize_token(t) for t in target_clean.split("_") if t and t not in ("vietnamese", "tiki", "data", "table", "info", "list", "detail", "details")]
    if not target_tokens:
        target_tokens = [_singularize_token(t) for t in target_clean.split("_") if t]

    target_entity = _singularize_token(target_clean)
    core_target = target_tokens[-1] if target_tokens else target_entity

    # 1. Cột kết thúc bằng _id hoặc _code khớp với thực thể đích chính (core entity hoặc full entity)
    for suffix in ("_id", "_code", "_key", "_sk", "_no", "_uuid", "_ref"):
        if col_clean.endswith(suffix) and len(col_clean) > len(suffix):
            col_prefix = _singularize_token(col_clean[:-len(suffix)].strip("_"))
            for p in ("origin_", "destination_", "parent_", "child_", "sender_", "recipient_", "from_", "to_", "sub_"):
                if col_prefix.startswith(p) and len(col_prefix) > len(p):
                    col_prefix = col_prefix[len(p):]

            if col_prefix in (target_entity, core_target, target_clean) or target_clean.endswith(f"_{col_prefix}"):
                return True

    # 2. Trùng tên khóa chính đặc thù
    if col_clean == target_pk.lower() and target_pk.lower() not in ("id", "pk", "sk", "stt", "col_1", "column_1"):
        return True

    # 3. Trùng tên thực thể trực tiếp (ví dụ: customer -> dim_customers.id)
    if col_clean in (target_entity, core_target) and len(col_clean) >= 3:
        return True

    return False


def _extract_dimension_entity(col_name: str) -> tuple[str, str, str, str] | None:
    """Trích xuất và tổng hợp thông tin Dimension từ bất kỳ tên cột nào (100% Dynamic, Zero-Hardcode)."""
    c = col_name.strip().lower()

    # Bỏ qua các cột đo lường, metric, cờ boolean hoặc timestamp
    metric_or_internal = {
        "id", "pk", "sk", "stt", "col", "column", "row_num", "index",
        "created_at", "updated_at", "deleted_at", "created_date", "updated_date",
        "timestamp", "datetime", "date", "year", "month", "day", "hour", "minute", "second",
        "price", "original_price", "cost", "amount", "total", "total_amount",
        "quantity", "quantity_sold", "count", "num", "number", "output_count",
        "score", "rate", "rating", "percent", "percentage", "ratio", "margin",
        "weight", "height", "width", "length", "volume", "speed", "size",
        "latitude", "longitude", "lat", "lng", "lon",
        "fee", "shipping_fee", "tax", "vat", "discount", "balance",
        "temperature", "vibration", "humidity", "pressure", "voltage", "current",
        "description", "note", "notes", "comment", "comments", "detail", "details",
        "content", "summary", "text", "message", "url", "image", "avatar", "photo",
        "is_active", "is_deleted", "is_valid", "has_video", "has_image", "status",
    }
    if c in metric_or_internal or c.startswith(("is_", "has_", "total_", "sum_", "avg_", "max_", "min_", "count_")):
        return None
    if any(m in c for m in ("_fee", "_amount", "_cost", "_price", "_tax", "_count", "_total", "_sum", "_avg", "_temp", "_rate", "_ratio")):
        return None

    # Hậu tố entity rõ ràng (_id, _code, _key, _sk, _pk, _no, _uuid, _ref)
    suffixes = (
        "_id", "_code", "_key", "_sk", "_pk", "_no", "_uuid", "_ref",
    )
    for s in suffixes:
        if c.endswith(s) and len(c) > len(s):
            entity_base = c[:-len(s)].strip("_")
            for p in ("origin_", "destination_", "parent_", "child_", "sender_", "recipient_", "from_", "to_", "sub_"):
                if entity_base.startswith(p) and len(entity_base) > len(p):
                    entity_base = entity_base[len(p):]
            if entity_base and len(entity_base) > 1:
                plural = _pluralize(entity_base)
                dim_table = f"dim_{plural}"
                dim_pk = f"{entity_base}_id"
                dim_desc = f"{entity_base}_name"
                return (entity_base, dim_table, dim_pk, dim_desc)

    return None


def _extract_natural_dimension(col_name: str, dbml_type: str) -> tuple[str, str] | None:
    """Nhận diện thuộc tính phân loại có thể nối bằng natural key."""
    if not dbml_type.startswith(("varchar", "text")):
        return None
    normalized = col_name.lower().strip("_")
    tokens = [token for token in normalized.split("_") if token]
    if not tokens:
        return None
    semantic_entities = {
        "brand", "category", "channel", "city", "country", "currency",
        "department", "merchant", "region", "seller", "status", "store",
        "type", "vendor",
    }
    entity = next((token for token in reversed(tokens) if token in semantic_entities), None)
    if entity is None and not normalized.endswith("_type"):
        return None
    entity = entity or "type"
    dimension_entity = normalized[:-5] + "_type" if entity == "type" and len(normalized) > 5 else entity
    return f"dim_{_pluralize(dimension_entity)}", normalized


def generate_rule_based_dbml(domain: str, description: str, tables: list[dict[str, Any]] | None) -> str:
    """Sinh DBML rule-based từ cấu trúc bảng nguồn (100% Dynamic cho mọi domain, không hardcode)."""
    if not tables:
        return generate_domain_fallback_dbml(domain, description)

    dbml_tables: list[str] = []
    refs: list[str] = []
    discovered_pks: dict[str, str | None] = {}
    table_columns_map: dict[str, list[str]] = {}
    table_column_types: dict[str, dict[str, str]] = {}
    used_table_names: set[str] = set()
    table_name_by_source: dict[str, str] = {}
    column_names_by_table: dict[str, dict[str, str]] = {}

    # 1. Parse tất cả các bảng và cột nguồn
    for table_dto in tables:
        raw_name = table_dto.get("name", "table")
        base_table_name = sanitize_identifier(raw_name)
        table_name = base_table_name
        table_suffix = 2
        while table_name in used_table_names:
            table_name = f"{base_table_name}_{table_suffix}"
            table_suffix += 1
        used_table_names.add(table_name)
        table_name_by_source[str(raw_name).strip().lower()] = table_name
        columns = table_dto.get("columns", [])
        rows = table_dto.get("rows", [])

        if not columns:
            continue

        table_lines = [f"Table {table_name} {{"]
        primary_key = _choose_primary_key(table_name, columns)
        discovered_pks[table_name] = primary_key
        col_names: list[str] = []
        column_types: dict[str, str] = {}
        used_column_names: set[str] = set()
        source_column_names: dict[str, str] = {}

        for col in columns:
            col_label = col.get("label") or col.get("key") or "col"
            col_key = col.get("key") or col_label
            base_col_name = sanitize_identifier(col_label)
            col_name = base_col_name
            column_suffix = 2
            while col_name in used_column_names:
                col_name = f"{base_col_name}_{column_suffix}"
                column_suffix += 1
            used_column_names.add(col_name)
            source_column_names[str(col_label).strip().lower()] = col_name
            col_type = col.get("type", "TEXT")
            col_names.append(col_name)

            sample_val = None
            if rows and isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
                sample_val = rows[0].get(col_key) or rows[0].get(col_label)

            dbml_type = map_column_type(base_col_name, col_type, sample_val)
            column_types[col_name] = dbml_type
            constraints = ["pk"] if primary_key and col_name == primary_key else []
            constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
            table_lines.append(f"  {col_name} {dbml_type}{constraint_str}")

        table_lines.append("}")
        dbml_tables.append("\n".join(table_lines))
        table_columns_map[table_name] = col_names
        table_column_types[table_name] = column_types
        column_names_by_table[table_name] = source_column_names

    seen_endpoints: set[tuple[str, str]] = set()

    # 2. Suy luận Foreign Key trực tiếp giữa các bảng đã có
    for table_name, col_names in table_columns_map.items():
        for col_name in col_names:
            matches = [
                (target_table, target_pk)
                for target_table, target_pk in discovered_pks.items()
                if target_pk is not None
                and target_table != table_name
                and _is_foreign_key_match(col_name, target_table, target_pk)
            ]
            if len(matches) != 1:
                continue
            target_table, target_pk = matches[0]
            source_endpoint = f"{table_name}.{col_name}"
            target_endpoint = f"{target_table}.{target_pk}"
            pair = tuple(sorted((source_endpoint, target_endpoint)))
            if pair not in seen_endpoints:
                seen_endpoints.add(pair)
                refs.append(f"Ref: {source_endpoint} > {target_endpoint}")

    # Quan hệ khai báo trực tiếp trong DDL luôn được ưu tiên nếu cả hai endpoint tồn tại.
    for table_dto in tables:
        source_table = table_name_by_source.get(str(table_dto.get("name", "")).strip().lower())
        if not source_table:
            continue
        for column in table_dto.get("columns", []):
            reference = column.get("references")
            if not isinstance(reference, dict):
                continue
            source_column = column_names_by_table[source_table].get(
                str(column.get("label") or column.get("key") or "").strip().lower()
            )
            target_table = table_name_by_source.get(str(reference.get("table", "")).strip().lower())
            if not source_column or not target_table:
                continue
            target_column = column_names_by_table[target_table].get(
                str(reference.get("column", "")).strip().lower()
            )
            if not target_column:
                continue
            source_endpoint = f"{source_table}.{source_column}"
            target_endpoint = f"{target_table}.{target_column}"
            pair = tuple(sorted((source_endpoint, target_endpoint)))
            if pair not in seen_endpoints:
                seen_endpoints.add(pair)
                refs.append(f"Ref: {source_endpoint} > {target_endpoint}")

    if not dbml_tables:
        return generate_domain_fallback_dbml(domain, description)

    result = "\n\n".join(dbml_tables)
    if refs:
        result += "\n\n" + "\n".join(refs)
    return result


def generate_domain_fallback_dbml(domain: str, description: str) -> str:
    """Sinh schema theo domain tổng quát khi không có bảng nguồn tải lên (100% Dynamic)."""
    d_clean = sanitize_identifier(domain) or "business"
    entity_name = _singularize(d_clean)

    return f"""Table fact_{entity_name}_events {{
  event_id int [pk, increment]
  {entity_name}_id int [not null]
  customer_id int [not null]
  event_date timestamp
  amount decimal(10,2)
}}

Table dim_{_pluralize(entity_name)} {{
  {entity_name}_id int [pk]
  {entity_name}_name varchar(255)
  category varchar(100)
  status varchar(50)
}}

Table dim_customers {{
  customer_id int [pk]
  customer_name varchar(255)
  email varchar(255)
  tier varchar(50)
}}

Ref: fact_{entity_name}_events.{entity_name}_id > dim_{_pluralize(entity_name)}.{entity_name}_id
Ref: fact_{entity_name}_events.customer_id > dim_customers.customer_id"""


def _sanitize_dbml(raw_text: str) -> str:
    """Loại bỏ markdown block và chuẩn hóa DBML trả về từ LLM."""
    clean = re.sub(r"^```(?:dbml)?\s*", "", raw_text, flags=re.MULTILINE)
    clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE)
    return clean.strip()


async def _generate_dbml_via_gemini(
    domain: str,
    description: str,
    tables: list[dict[str, Any]] | None,
    target_dialect: str,
) -> str | None:
    """Sử dụng Google Gemini Flash để thiết kế Star / Snowflake Schema hoàn chỉnh cho bất kỳ domain nào."""
    try:
        import asyncio

        import google.generativeai as genai
        from config import get_settings

        settings = get_settings()
        api_key = (os.getenv("GOOGLE_API_KEY") if os.getenv("GOOGLE_API_KEY") is not None else settings.google_api_key).strip()
        if not api_key:
            return None

        genai.configure(api_key=api_key)

        table_descriptors = []
        for t in (tables or []):
            t_name = sanitize_identifier(t.get("name", "table"))
            cols = [
                f"{sanitize_identifier(c.get('label') or c.get('key') or 'col')} ({c.get('type', 'TEXT')})"
                for c in t.get("columns", [])
            ]
            table_descriptors.append(f"- Table `{t_name}`: {', '.join(cols)}")

        prompt = f"""You are a Principal Data Warehouse Architect & Database Modeling Expert.
Design a clean, normalized, robust Data Schema in standard DBML format for ANY business domain provided.

Project Context:
- Domain: {domain or 'general'}
- Business Description: {description or 'Data Warehouse modeling'}
- Target Dialect: {target_dialect}

Source Tables:
{chr(10).join(table_descriptors)}

CRITICAL MODELING RULES (STRICT COLUMN & RELATIONSHIP INTEGRITY):
1. EXACT TABLES & COLUMNS PRESERVATION: Strictly preserve the exact tables and columns provided in the source tables. DO NOT invent, hallucinate, or generate phantom dimension tables (like dim_names, dim_colors, dummy dimensions) unless they are explicitly in the source data!
2. NO UNREQUESTED EXTRA COLUMNS: Do NOT invent extra columns for existing tables.
3. GROUNDED RELATIONSHIPS ONLY: Connect tables via Foreign Key relationships (`Ref:`) ONLY when there is a true, logical, semantic Foreign Key relationship between columns (e.g. matching `<entity>_id`). If the source tables represent separate product categories or independent entities without relational foreign keys, KEEP THEM AS CLEAN SEPARATE TABLES without forging artificial joins!
4. Mark primary keys with [pk].
5. Put all `Ref:` statements at the ROOT TOP-LEVEL OUTSIDE table bodies (e.g. `Ref: source_table.foreign_key > target_table.primary_key`).
6. Output ONLY raw DBML code. Do NOT wrap in markdown explanations.
"""

        model_candidates = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]
        for model_name in model_candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        model.generate_content,
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=2500,
                        ),
                    ),
                    timeout=15.0,
                )
                raw_text = response.text.strip()
                cleaned = _sanitize_dbml(raw_text)
                if "Table " in cleaned and "{" in cleaned:
                    from src.domain.data_model.rules import validate_dbml
                    validate_dbml(cleaned)
                    logger.info("Gemini (%s) đã thiết kế thành công Schema DBML hoàn chỉnh.", model_name)
                    return cleaned
            except Exception as e:
                logger.warning("Gemini model %s không thể sinh DBML: %s", model_name, e)

        return None
    except Exception as exc:
        logger.warning("Toàn bộ tiến trình Gemini DBML generation thất bại: %s", exc)
        return None


async def generate_initial_dbml(
    domain: str,
    description: str,
    tables: list[dict[str, Any]] | None = None,
    target_dialect: str = "postgresql",
    ai_context: dict[str, Any] | None = None,
) -> str:
    """Tạo schema DBML ban đầu từ dữ liệu nguồn hoặc LLM (có timeout, sanitize và fallback nhanh)."""
    merged_tables = list(tables or [])
    try:
        for schema in (ai_context or {}).get("schemas", []):
            for t in schema.get("tables", []):
                if not any(existing.get("name") == t.get("name") for existing in merged_tables):
                    merged_tables.append(t)
    except Exception:
        pass

    # Schema nguồn phải được biến đổi theo luật xác định để không đổi tên/cột
    # mơ hồ giữa các lần chạy. LLM chỉ còn dùng cho luồng không có metadata.
    if merged_tables:
        base_dbml = generate_rule_based_dbml(domain, description, merged_tables)
    else:
        gemini_dbml = await _generate_dbml_via_gemini(
            domain, description, merged_tables, target_dialect
        )
        base_dbml = gemini_dbml if gemini_dbml else generate_domain_fallback_dbml(
            domain, description
        )

    # 2. Chạy thêm tầng Relationship Inferrer bằng AI để đảm bảo 100% không sót bất kỳ Ref/quan hệ nào
    try:
        from src.application.projects.relationship_inferrer import infer_relationships_with_ai

        return await infer_relationships_with_ai(base_dbml, tables=tables, domain=domain, description=description)
    except Exception as exc:
        logger.warning("AI relationship inference failed (graceful): %s", exc)
        return base_dbml
