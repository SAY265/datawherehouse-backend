"""Module suy luận quan hệ (Foreign Key) giữa các bảng bằng Google Gemini AI kết hợp Graph Topology & Semantic Heuristics.

Phân tích toàn diện cấu trúc bảng, kiểu dữ liệu và ngữ nghĩa nghiệp vụ để tự động
kết nối các khóa chính - khóa ngoại (`Ref:`), xây dựng sơ đồ ERD hoàn chỉnh (Star/Snowflake schema).
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any

from src.common.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class RelationshipAgentWarning:
    """Cảnh báo có cấu trúc để UI chỉ ra quan hệ chưa thể tự nối."""

    code: str
    message: str
    table_name: str
    column_name: str
    expected_table: str | None = None


@dataclass(frozen=True)
class RelationshipAgentResult:
    """Kết quả chạy Relationship Agent cục bộ, không làm lộ schema ra ngoài."""

    dbml: str
    added_refs: tuple[dict[str, str], ...]
    warnings: tuple[RelationshipAgentWarning, ...]

# ---------------------------------------------------------------------------
# Prompt template chuyên sâu về Data Modeling & Schema Design
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a Principal Data Warehouse Architect & Database Modeling Expert.
Your task is to analyze a list of database tables, their columns, and data types, then identify ONLY TRUE, VALID Foreign Key (FK) relationships.

CRITICAL RULES FOR RELATIONSHIP INFERENCE (STRICT CONTROL - NO LOOSE/PASSIVE CONNECTIONS):
1. EXACT OR EXPLICIT FK MATCH ONLY:
   - Connect a column ONLY if it is an explicit Foreign Key (e.g., `orders.customer_id` > `customers.customer_id`, `fact_trips.passenger_id` > `passengers.passenger_id`, `fact_trips.driver_id` > `drivers.driver_id`, `vehicles.driver_id` > `drivers.driver_id`).
   - The child column (`from_column`) MUST be an ID/Key column (ending in `_id`, `_code`, `_key`, `_uuid`, `_ref`, `_no`, or matching the parent PK name).
2. NEVER CONNECT UNRELATED INDEPENDENT MASTER TABLES:
   - Do NOT connect two parallel dimension/master tables directly if there is no genuine parent-child hierarchy (e.g., NEVER connect `customers` to `drivers`, NEVER connect `passengers` to `drivers`, NEVER connect `users` to `products`).
3. NO PASSIVE OR ARBITRARY ATTRIBUTE MATCHING:
   - NEVER connect descriptive or attribute columns (such as `name`, `status`, `type`, `description`, `phone_number`, `score`, `amount`, `created_at`) to an ID column of another table.
4. STRICT CARDINALITY & DIRECTION:
   - Always format as Many-to-One: `from_table.foreign_key_column > to_table.primary_key_column`
   - `from_table` MUST be the Child / Fact table containing the foreign key reference.
   - `to_table` MUST be the Parent / Dimension table whose Primary Key is being referenced.
   - `to_column` MUST be the Primary Key (`[PK]`) of `to_table`.
5. TYPE COMPATIBILITY:
   - Only connect columns with matching/compatible data types (e.g., `int` with `int`, `uuid` with `uuid`, `varchar` with `varchar`).
6. GROUNDED IN PROVIDED SCHEMA:
   - Strictly reference table and column names that exist in the input schema. Never hallucinate or assume non-existent columns.
7. NO CIRCULAR LOOPS:
   - Do NOT create bidirectional or circular cycles (A -> B and B -> A).

RETURN FORMAT:
Return ONLY a valid JSON array. Each element must have this exact structure:
[
  {
    "from_table": "table_name_a",
    "from_column": "column_name_a",
    "to_table": "table_name_b",
    "to_column": "column_name_b"
  }
]

If no relationships can be identified, return: []
Do NOT include explanations, markdown formatting, or code blocks. Output raw JSON only."""


def _extract_table_summaries(
    dbml: str,
    tables: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Trích xuất tên bảng, danh sách cột và kiểu dữ liệu từ DBML hoặc source tables."""
    summaries: list[dict[str, Any]] = []

    # 1. Thử dùng PyDBML parser trước
    try:
        from pydbml import PyDBML

        database = PyDBML(dbml)
        for table in database.tables:
            table_name = str(table.name).strip('"`\'')
            cols_info: list[dict[str, str]] = []
            pk_col: str | None = None
            for col in table.columns:
                c_name = str(col.name).strip('"`\'')
                c_type = str(col.type).strip('"`\'')
                is_pk = bool(col.pk)
                if is_pk and not pk_col:
                    pk_col = c_name
                cols_info.append({"name": c_name, "type": c_type, "is_pk": str(is_pk).lower()})
            if cols_info:
                summaries.append({
                    "name": table_name,
                    "pk": pk_col,
                    "columns": [c["name"] for c in cols_info],
                    "columns_with_types": cols_info,
                })
        if summaries:
            return summaries
    except Exception:
        pass

    # 2. Regex fallback (hỗ trợ cả Table "name" và Table name)
    table_pattern = re.compile(
        r'Table\s+(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\s*\{([^}]*)\}', re.IGNORECASE | re.DOTALL
    )
    for match in table_pattern.finditer(dbml):
        raw_tname = match.group(1) or match.group(2) or match.group(3) or ""
        table_name = raw_tname.strip('"`\'')
        body = match.group(4)
        columns: list[dict[str, str]] = []
        pk_column: str | None = None

        for line in body.strip().splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("//"):
                continue
            parts = line_str.split()
            if parts:
                col_name = parts[0].strip('"`\'')
                col_type = parts[1].strip('"`\'') if len(parts) > 1 else "varchar(255)"
                # Bỏ brackets [pk] nếu dính vào type
                col_type = re.sub(r"\[.*?\]", "", col_type).strip() or "varchar(255)"
                is_pk = any(k in line_str.lower() for k in ("[pk", "pk,", ", pk", ",pk", "primary key"))
                if is_pk and not pk_column:
                    pk_column = col_name
                columns.append({"name": col_name, "type": col_type, "is_pk": str(is_pk).lower()})

        if columns:
            summaries.append({
                "name": table_name,
                "pk": pk_column,
                "columns": [c["name"] for c in columns],
                "columns_with_types": columns,
            })

    if summaries:
        return summaries

    # 3. Fallback: dùng source tables
    if tables:
        for t in tables:
            name = str(t.get("name", "")).strip('"`\'')
            cols: list[dict[str, str]] = []
            for c in t.get("columns", []):
                col_name = str(c.get("label") or c.get("key") or "").strip('"`\'')
                col_type = str(c.get("type") or "TEXT").strip('"`\'')
                if col_name:
                    cols.append({"name": col_name, "type": col_type, "is_pk": "false"})
            if name and cols:
                summaries.append({
                    "name": name,
                    "pk": None,
                    "columns": [c["name"] for c in cols],
                    "columns_with_types": cols,
                })

    return summaries


def _extract_existing_refs(dbml: str) -> set[tuple[str, str]]:
    """Trích xuất các endpoint pair đã có trong DBML."""
    refs: set[tuple[str, str]] = set()
    ref_pattern = re.compile(
        r'Ref\s*:\s*(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\.(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\s*[<>-]\s*(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\.(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))',
        re.IGNORECASE,
    )
    for m in ref_pattern.finditer(dbml):
        t1 = (m.group(1) or m.group(2) or m.group(3) or "").strip('"`\'').lower()
        c1 = (m.group(4) or m.group(5) or m.group(6) or "").strip('"`\'').lower()
        t2 = (m.group(7) or m.group(8) or m.group(9) or "").strip('"`\'').lower()
        c2 = (m.group(10) or m.group(11) or m.group(12) or "").strip('"`\'').lower()
        if t1 and c1 and t2 and c2:
            pair = tuple(sorted((f"{t1}.{c1}", f"{t2}.{c2}")))
            refs.add(pair)  # type: ignore[arg-type]
    return refs


def _build_user_prompt(
    tables_summary: list[dict[str, Any]],
    domain: str,
    description: str,
) -> str:
    """Xây dựng prompt mô tả bảng + kiểu dữ liệu + khóa chính cho Gemini."""
    lines = [f"Domain: {domain or 'general'}"]
    if description:
        lines.append(f"Business Description: {description}")
    lines.append("")
    lines.append("Tables & Columns Schema:")
    for t in tables_summary:
        cols_desc = []
        for c in t.get("columns_with_types", []):
            pk_mark = " [PK]" if c.get("name") == t.get("pk") else ""
            cols_desc.append(f"{c.get('name')} ({c.get('type', 'varchar')}{pk_mark})")
        lines.append(f"- Table `{t['name']}`: {', '.join(cols_desc)}")

    return "\n".join(lines)


def _parse_gemini_response(text: str) -> list[dict[str, str]]:
    """Parse JSON array từ response text của Gemini."""
    cleaned = text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            valid_items = []
            for r in result:
                if isinstance(r, dict) and all(k in r for k in ("from_table", "from_column", "to_table", "to_column")):
                    valid_items.append({
                        "from_table": str(r["from_table"]).strip(),
                        "from_column": str(r["from_column"]).strip(),
                        "to_table": str(r["to_table"]).strip(),
                        "to_column": str(r["to_column"]).strip(),
                    })
            return valid_items
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def _validate_and_filter_refs(
    refs: list[dict[str, str]],
    tables_summary: list[dict[str, Any]],
    existing_refs: set[tuple[str, str]],
) -> list[dict[str, str]]:
    """Thẩm định tính hợp lệ đồ thị quan hệ: tồn tại cột, chống tự nối, chống vòng lặp."""
    # Map table_name -> map(col_name -> type)
    table_cols: dict[str, dict[str, str]] = {}
    table_pks: dict[str, str] = {}

    for t in tables_summary:
        t_name = t["name"].lower()
        raw_pk = t.get("pk")
        if raw_pk:
            table_pks[t_name] = str(raw_pk).lower()
        cols_map: dict[str, str] = {}
        for c in t.get("columns_with_types", []):
            cols_map[c["name"].lower()] = c.get("type", "varchar(255)").lower()
        table_cols[t_name] = cols_map

    valid_refs: list[dict[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set(existing_refs)
    used_sources = {endpoint for pair in existing_refs for endpoint in pair}

    for ref in refs:
        ft = ref["from_table"].lower()
        fc = ref["from_column"].lower()
        tt = ref["to_table"].lower()
        tc = ref["to_column"].lower()

        # 1. Loại bỏ tự tham chiếu cùng bảng
        if ft == tt:
            continue

        # 2. Đảm bảo cả hai bảng và cột đều tồn tại
        if ft not in table_cols or tt not in table_cols:
            continue
        if fc not in table_cols[ft] or tc not in table_cols[tt]:
            continue

        # Quan hệ do agent tạo phải trỏ đến khóa chính và có kiểu tương thích.
        if tt not in table_pks or tc != table_pks[tt]:
            continue
        if not _types_are_compatible(table_cols[ft][fc], table_cols[tt][tc]):
            continue

        # 3. Tránh trùng lặp endpoint pair (cả chiều thuận và nghịch)
        source_ep = f"{ft}.{fc}"
        target_ep = f"{tt}.{tc}"
        pair = tuple(sorted((source_ep, target_ep)))
        if pair in seen_pairs or source_ep in used_sources:
            continue

        # 4. Tìm lại tên gốc đúng hoa thường từ tables_summary
        orig_ft = next((t["name"] for t in tables_summary if t["name"].lower() == ft), ft)
        orig_tt = next((t["name"] for t in tables_summary if t["name"].lower() == tt), tt)
        orig_fc = next((c for c in table_cols[ft] if c == fc), fc)
        orig_tc = next((c for c in table_cols[tt] if c == tc), tc)

        seen_pairs.add(pair)
        used_sources.add(source_ep)
        valid_refs.append({
            "from_table": orig_ft,
            "from_column": orig_fc,
            "to_table": orig_tt,
            "to_column": orig_tc,
        })

    return valid_refs


def _type_family(data_type: str) -> str:
    """Chuẩn hóa kiểu DBML về nhóm tương thích cho khóa ngoại."""
    normalized = re.sub(r"\s+", "", data_type.lower())
    base = normalized.split("(", 1)[0]
    if base in {"int", "integer", "smallint", "bigint", "serial", "bigserial"}:
        return "integer"
    if base in {"varchar", "char", "character", "text", "string"}:
        return "string"
    if base in {"uuid"}:
        return "uuid"
    if base in {"decimal", "numeric", "float", "double", "real"}:
        return "number"
    if base in {"date", "datetime", "timestamp", "timestamptz"}:
        return "datetime"
    return base


def _types_are_compatible(source_type: str, target_type: str) -> bool:
    return _type_family(source_type) == _type_family(target_type)


def _singularize_token(word: str) -> str:
    """Chuẩn hóa từ tiếng Anh về dạng số ít chuẩn (Lemmatization/Stemming)."""
    w = word.lower().strip()
    if not w:
        return ""
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"  # categories -> category, companies -> company, accessories -> accessory
    if w.endswith(("sses", "shes", "ches", "xes", "zzes")):
        return w[:-2]  # classes -> class, addresses -> address, boxes -> box, branches -> branch, wishes -> wish
    if w.endswith("ves") and len(w) > 4:
        return w[:-3] + "f"  # shelves -> shelf, knives -> knife
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]  # suitcases -> suitcase, products -> product, users -> user, orders -> order, items -> item
    return w


def _extract_table_entities(table_name: str) -> set[str]:
    """Trích xuất tất cả các thực thể tiềm năng từ tên bảng (hỗ trợ composite name và tiền tố)."""
    clean = table_name.lower().split(".")[-1]
    for prefix in ("fact_", "dim_", "tb_", "tbl_", "table_", "v_", "stg_", "raw_", "source_", "src_", "public_"):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]

    # Loại bỏ tiền tố tên dự án / nguồn dữ liệu thông dụng
    tokens = [t for t in clean.split("_") if t and t not in ("vietnamese", "tiki", "data", "table", "info", "list", "detail", "details")]
    if not tokens:
        tokens = [t for t in clean.split("_") if t]

    entities: set[str] = set()

    for t in tokens:
        sing = _singularize_token(t)
        if sing:
            entities.add(sing)
            entities.add(t)

    # Cụm 2 token liền kề
    for i in range(len(tokens) - 1):
        pair_sing = f"{_singularize_token(tokens[i])}_{_singularize_token(tokens[i+1])}"
        entities.add(pair_sing)
        entities.add(f"{tokens[i]}_{tokens[i+1]}")

    full_sing = _singularize_token(clean)
    entities.add(clean)
    entities.add(full_sing)

    return entities


def _infer_semantic_rule_based_refs(
    tables_summary: list[dict[str, Any]],
    existing_refs: set[tuple[str, str]],
) -> list[dict[str, str]]:
    """Suy luận quan hệ rule-based chặt chẽ, chống nối bừa/thụ động giữa các bảng không liên quan."""
    inferred: list[dict[str, str]] = []

    # Map các từ đồng nghĩa chuẩn xác theo từng thực thể nghiệp vụ riêng biệt (KHÔNG gộp chéo các thực thể khác nhau)
    strict_entity_synonyms: dict[str, set[str]] = {
        "customer": {"customer", "client", "buyer", "purchaser"},
        "user": {"user", "account", "member"},
        "driver": {"driver", "chauffeur"},
        "passenger": {"passenger", "traveler", "commuter", "rider"},
        "vehicle": {"vehicle", "car", "taxi", "bike", "truck"},
        "merchant": {"merchant", "seller", "vendor", "store", "shop"},
        "product": {"product", "item", "article", "sku", "merchandise"},
        "category": {"category", "catalogue", "sub_category", "department"},
        "order": {"order", "invoice", "booking", "trip", "ride", "transaction"},
        "brand": {"brand", "manufacturer", "maker"},
    }

    for t1 in tables_summary:
        t1_name = t1["name"]
        t1_cols = t1["columns"]
        t1_pk = str(t1.get("pk") or "").lower()

        for col in t1_cols:
            col_lower = col.lower().strip('"`\'')
            # 1. Bỏ qua nếu cột này chính là Khóa chính của bảng nguồn t1
            if col_lower == t1_pk:
                continue

            for t2 in tables_summary:
                t2_name = t2["name"]
                if t1_name.lower() == t2_name.lower():
                    continue

                t2_pk = t2.get("pk")
                if not t2_pk:
                    continue
                t2_pk_lower = str(t2_pk).lower().strip('"`\'')
                target_clean = t2_name.split(".")[-1].lower().strip('"`\'')
                for prefix in ("fact_", "dim_", "tb_", "tbl_", "table_", "v_", "stg_", "raw_", "source_", "src_", "public_"):
                    if target_clean.startswith(prefix):
                        target_clean = target_clean[len(prefix):]
                        break

                t2_tokens = [_singularize_token(t) for t in target_clean.split("_") if t and t not in ("vietnamese", "tiki", "data", "table", "info", "list", "detail", "details")]
                if not t2_tokens:
                    t2_tokens = [_singularize_token(t) for t in target_clean.split("_") if t]

                target_entity = _singularize_token(target_clean)
                core_target = t2_tokens[-1] if t2_tokens else target_entity

                match = False

                # a) Khớp khóa ngoại với hậu tố (_id, _code, _key, _sk, _no, _uuid, _ref, _fk)
                for suffix in ("_id", "_code", "_key", "_sk", "_no", "_uuid", "_ref", "_fk"):
                    if col_lower.endswith(suffix) and len(col_lower) > len(suffix):
                        entity_base = _singularize_token(col_lower[:-len(suffix)].strip("_"))
                        for p in ("origin_", "destination_", "parent_", "child_", "sender_", "recipient_", "from_", "to_", "sub_"):
                            if entity_base.startswith(p) and len(entity_base) > len(p):
                                entity_base = entity_base[len(p):]

                        # 1. Khớp trực tiếp với core entity hoặc full entity của t2
                        if entity_base in (target_entity, core_target, target_clean) or target_clean.endswith(f"_{entity_base}"):
                            match = True
                            break
                        # 2. Khớp qua synonym của CHÍNH thực thể đích (chỉ trong tập từ đồng nghĩa của core_target/target_entity)
                        for domain_key, syn_set in strict_entity_synonyms.items():
                            if (core_target == domain_key or target_entity == domain_key or core_target in syn_set or target_entity in syn_set):
                                if entity_base in syn_set:
                                    match = True
                                    break
                        if match:
                            break

                # b) Khớp trực tiếp tên cột với PK đặc thù của t2 (ví dụ: fact_trips.passenger_id khớp với passengers.passenger_id)
                if not match and col_lower == t2_pk_lower and t2_pk_lower not in ("id", "pk", "sk", "stt", "col_1", "column_1"):
                    # Đảm bảo entity base của cột tương ứng với bảng đích
                    col_entity = _foreign_key_entity(col_lower)
                    if col_entity in (target_entity, core_target, target_clean) or (col_entity and col_entity in _extract_table_entities(t2_name)):
                        match = True

                if match:
                    inferred.append({
                        "from_table": t1_name,
                        "from_column": col,
                        "to_table": t2_name,
                        "to_column": t2_pk,
                    })

    # Ưu tiên khớp tên thực thể chính xác trước
    inferred.sort(
        key=lambda ref: int(
            (_foreign_key_entity(ref["from_column"]) or "")
            in _extract_table_entities(ref["to_table"])
        ),
        reverse=True,
    )
    return _validate_and_filter_refs(inferred, tables_summary, existing_refs)


def _merge_refs_into_dbml(
    dbml: str,
    new_refs: list[dict[str, str]],
) -> str:
    """Thêm các Ref: mới vào cuối DBML."""
    if not new_refs:
        return dbml

    added = [f"Ref: {r['from_table']}.{r['from_column']} > {r['to_table']}.{r['to_column']}" for r in new_refs]
    return dbml.rstrip() + "\n\n" + "\n".join(added)


_FK_SUFFIXES = ("_id", "_code", "_key", "_sk", "_no", "_uuid", "_ref")


def _foreign_key_entity(column_name: str) -> str | None:
    """Lấy thực thể được nhắc tới trong một tên cột có dáng khóa ngoại."""
    normalized = column_name.lower().strip()
    for suffix in _FK_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) > len(suffix):
            entity = _singularize_token(normalized[: -len(suffix)].strip("_"))
            for prefix in (
                "origin_", "destination_", "parent_", "child_", "sender_",
                "recipient_", "from_", "to_", "sub_",
            ):
                if entity.startswith(prefix) and len(entity) > len(prefix):
                    entity = entity[len(prefix) :]
            return entity or None
    return None


def _pluralize_token(word: str) -> str:
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def _extract_ref_source_endpoints(dbml: str) -> set[str]:
    pattern = re.compile(
        r'Ref\s*:\s*(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\.(?:"([^"]+)"|\'([^\']+)\'|([\w.]+))\s*[>-]',
        re.IGNORECASE,
    )
    endpoints = set()
    for m in pattern.finditer(dbml):
        t = (m.group(1) or m.group(2) or m.group(3) or "").strip('"`\'').lower()
        c = (m.group(4) or m.group(5) or m.group(6) or "").strip('"`\'').lower()
        if t and c:
            endpoints.add(f"{t}.{c}")
    return endpoints


def _build_relationship_warnings(
    dbml: str,
    tables_summary: list[dict[str, Any]],
) -> list[RelationshipAgentWarning]:
    """Cảnh báo các cột giống FK nhưng không thể nối an toàn."""
    resolved_sources = _extract_ref_source_endpoints(dbml)
    warnings: list[RelationshipAgentWarning] = []

    for source in tables_summary:
        source_name = str(source["name"])
        source_pk = str(source.get("pk") or "").lower()
        source_types = {
            str(column["name"]).lower(): str(column.get("type", "varchar"))
            for column in source.get("columns_with_types", [])
        }
        for column_name in source.get("columns", []):
            column = str(column_name)
            if column.lower() == source_pk:
                continue
            entity = _foreign_key_entity(column)
            if not entity or f"{source_name}.{column}".lower() in resolved_sources:
                continue

            candidates = [
                target
                for target in tables_summary
                if str(target["name"]).lower() != source_name.lower()
                and entity in _extract_table_entities(str(target["name"]))
            ]
            expected_table = _pluralize_token(entity)
            compatible_candidates = []
            for target in candidates:
                raw_target_pk = target.get("pk")
                if not raw_target_pk:
                    continue
                target_pk = str(raw_target_pk)
                target_type = next(
                    (
                        str(item.get("type", "varchar"))
                        for item in target.get("columns_with_types", [])
                        if str(item.get("name", "")).lower() == target_pk.lower()
                    ),
                    "varchar",
                )
                if _types_are_compatible(source_types.get(column.lower(), "varchar"), target_type):
                    compatible_candidates.append(target)

            if candidates and not compatible_candidates:
                warnings.append(
                    RelationshipAgentWarning(
                        code="INCOMPATIBLE_RELATIONSHIP_TYPE",
                        message=(
                            f"Không thể nối {source_name}.{column}: kiểu dữ liệu không tương thích "
                            f"với khóa chính của bảng {candidates[0]['name']}."
                        ),
                        table_name=source_name,
                        column_name=column,
                        expected_table=str(candidates[0]["name"]),
                    )
                )
            elif not compatible_candidates:
                warnings.append(
                    RelationshipAgentWarning(
                        code="MISSING_REFERENCED_TABLE",
                        message=(
                            f"Không tìm thấy bảng đích cho {source_name}.{column}; "
                            f"hãy bổ sung hoặc đổi tên bảng {expected_table}."
                        ),
                        table_name=source_name,
                        column_name=column,
                        expected_table=expected_table,
                    )
                )

    return warnings


def run_relationship_agent(
    dbml: str,
    tables: list[dict[str, Any]] | None = None,
) -> RelationshipAgentResult:
    """Tự nối quan hệ bằng luật cục bộ và trả cảnh báo, không gọi dịch vụ ngoài."""
    tables_summary = _extract_table_summaries(dbml, tables)
    existing_refs = _extract_existing_refs(dbml)
    refs = (
        _infer_semantic_rule_based_refs(tables_summary, existing_refs)
        if len(tables_summary) >= 2
        else []
    )
    merged_dbml = _merge_refs_into_dbml(dbml, refs)

    from src.domain.data_model.rules import validate_dbml

    validate_dbml(merged_dbml)
    return RelationshipAgentResult(
        dbml=merged_dbml,
        added_refs=tuple(refs),
        warnings=tuple(_build_relationship_warnings(merged_dbml, tables_summary)),
    )


async def run_relationship_agent_with_ai(
    dbml: str,
    tables: list[dict[str, Any]] | None = None,
    domain: str = "",
    description: str = "",
) -> RelationshipAgentResult:
    """Tự nối quan hệ bằng AI kết hợp bộ luật và trả cảnh báo."""
    tables_summary = _extract_table_summaries(dbml, tables)
    if len(tables_summary) < 2:
        return RelationshipAgentResult(dbml=dbml, added_refs=(), warnings=())

    existing_refs = _extract_existing_refs(dbml)
    proposed_refs: list[dict[str, str]] = []

    try:
        from config import get_settings
        import os

        settings = get_settings()
        api_key = (os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else settings.openai_api_key).strip()
        base_url = (os.getenv("OPENAI_BASE_URL") if os.getenv("OPENAI_BASE_URL") is not None else settings.openai_base_url).strip()
        model_name = (os.getenv("MODEL_NAME") if os.getenv("MODEL_NAME") is not None else settings.model_name).strip()

        if api_key and not api_key.lower().startswith(("sk-placeholder", "sk-your-")):
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            from src.infrastructure.llm.data_model_insight_analyzer import LlmDataModelInsightAnalyzer

            resolved_base_url, resolved_model_name = LlmDataModelInsightAnalyzer._resolve_provider_config(
                api_key, base_url, model_name
            )

            model = ChatOpenAI(
                api_key=api_key,
                model=resolved_model_name,
                temperature=0.1,
                max_tokens=1500,
                base_url=resolved_base_url if resolved_base_url else None,
            )

            user_prompt = _build_user_prompt(tables_summary, domain, description)
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"

            try:
                response = await asyncio.wait_for(
                    model.ainvoke([HumanMessage(content=full_prompt)]),
                    timeout=30.0,
                )
                raw_text = str(response.content).strip()
                if raw_text:
                    proposed_refs = _parse_gemini_response(raw_text)
                    logger.info("AI (%s) đề xuất %d quan hệ khóa ngoại.", resolved_model_name, len(proposed_refs))
            except Exception as model_err:
                logger.warning("Primary AI model thất bại: %s", model_err)
    except Exception as exc:
        logger.warning("AI relationship agent lỗi: %s", exc)

    valid_refs = _validate_and_filter_refs(proposed_refs, tables_summary, existing_refs)
    refs_after_ai = set(existing_refs)
    for ref in valid_refs:
        refs_after_ai.add(
            tuple(
                sorted(
                    (
                        f"{ref['from_table']}.{ref['from_column']}".lower(),
                        f"{ref['to_table']}.{ref['to_column']}".lower(),
                    )
                )
            )
        )
    valid_refs.extend(_infer_semantic_rule_based_refs(tables_summary, refs_after_ai))

    merged_dbml = _merge_refs_into_dbml(dbml, valid_refs)
    try:
        from src.domain.data_model.rules import validate_dbml

        validate_dbml(merged_dbml)
    except Exception:
        merged_dbml = dbml

    return RelationshipAgentResult(
        dbml=merged_dbml,
        added_refs=tuple(valid_refs),
        warnings=tuple(_build_relationship_warnings(merged_dbml, tables_summary)),
    )


async def infer_relationships_with_ai(
    dbml: str,
    tables: list[dict[str, Any]] | None = None,
    domain: str = "",
    description: str = "",
) -> str:
    """Tự động phân tích và kết nối khóa ngoại (`Ref:`) cho toàn bộ schema DBML.

    Quy trình:
    1. Trích xuất metadata và các Ref: hiện có.
    2. Gọi Google Gemini 2.0 Flash phân tích quan hệ ngữ nghĩa.
    3. Fallback sang Semantic Rule-based Engine nếu AI gặp lỗi.
    4. Thẩm định đồ thị quan hệ (Topology, Type Compatibility, Unique endpoints).
    5. Merge Ref: vào DBML và kiểm tra cú pháp với Lark DBML parser.
    """
    tables_summary = _extract_table_summaries(dbml, tables)
    if len(tables_summary) < 2:
        logger.info("Chỉ có %d bảng, không cần suy luận quan hệ ngoại.", len(tables_summary))
        return dbml

    existing_refs = _extract_existing_refs(dbml)
    proposed_refs: list[dict[str, str]] = []

    # 1. Thử gọi AI
    try:
        from config import get_settings
        import os

        settings = get_settings()
        api_key = (os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else settings.openai_api_key).strip()
        base_url = (os.getenv("OPENAI_BASE_URL") if os.getenv("OPENAI_BASE_URL") is not None else settings.openai_base_url).strip()
        model_name = (os.getenv("MODEL_NAME") if os.getenv("MODEL_NAME") is not None else settings.model_name).strip()

        if api_key and not api_key.lower().startswith(("sk-placeholder", "sk-your-")):
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            from src.infrastructure.llm.data_model_insight_analyzer import LlmDataModelInsightAnalyzer

            resolved_base_url, resolved_model_name = LlmDataModelInsightAnalyzer._resolve_provider_config(
                api_key, base_url, model_name
            )

            model = ChatOpenAI(
                api_key=api_key,
                model=resolved_model_name,
                temperature=0.1,
                max_tokens=1500,
                base_url=resolved_base_url if resolved_base_url else None,
            )

            user_prompt = _build_user_prompt(tables_summary, domain, description)
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"

            try:
                import asyncio
                response = await asyncio.wait_for(
                    model.ainvoke([HumanMessage(content=full_prompt)]),
                    timeout=30.0,
                )
                raw_text = str(response.content).strip()
                if raw_text:
                    proposed_refs = _parse_gemini_response(raw_text)
                    logger.info("AI (%s) đề xuất %d quan hệ khóa ngoại.", resolved_model_name, len(proposed_refs))
            except Exception as model_err:
                logger.warning("Primary AI model %s thất bại (%s); kích hoạt 14B Fallback Model...", resolved_model_name, model_err)
                try:
                    from src.infrastructure.llm.fallback_14b_executor import invoke_with_14b_fallback

                    fb_response = await invoke_with_14b_fallback([HumanMessage(content=full_prompt)], timeout=5.0)
                    fb_raw_text = str(fb_response.content).strip()
                    if fb_raw_text:
                        proposed_refs = _parse_gemini_response(fb_raw_text)
                        logger.info("14B Fallback Model đề xuất %d quan hệ khóa ngoại.", len(proposed_refs))
                except Exception as fb_err:
                    logger.warning("14B Fallback Model cũng không khả dụng (%s).", fb_err)

    except Exception as exc:
        logger.warning("AI relationship inference gặp sự cố: %s. Kích hoạt Semantic Fallback.", exc)

    # 2. Luôn chạy bộ luật cục bộ để bù các quan hệ AI trả thiếu.
    valid_refs = _validate_and_filter_refs(proposed_refs, tables_summary, existing_refs)
    refs_after_ai = set(existing_refs)
    for ref in valid_refs:
        refs_after_ai.add(
            tuple(
                sorted(
                    (
                        f"{ref['from_table']}.{ref['from_column']}".lower(),
                        f"{ref['to_table']}.{ref['to_column']}".lower(),
                    )
                )
            )
        )
    valid_refs.extend(_infer_semantic_rule_based_refs(tables_summary, refs_after_ai))

    if not valid_refs:
        logger.info("Không có quan hệ mới nào cần bổ sung vào DBML.")
        return dbml

    # 3. Merge Ref vào DBML
    merged_dbml = _merge_refs_into_dbml(dbml, valid_refs)

    # 4. Kiểm định với Lark DBML parser
    try:
        from src.domain.data_model.rules import validate_dbml

        validate_dbml(merged_dbml)
        logger.info("Đã áp dụng thành công %d quan hệ Ref: vào DBML hoàn chỉnh.", len(valid_refs))
        return merged_dbml
    except Exception as parse_err:
        logger.warning("DBML sau khi thêm Ref bị lỗi cú pháp (%s), giữ nguyên DBML ban đầu.", parse_err)
        return dbml
