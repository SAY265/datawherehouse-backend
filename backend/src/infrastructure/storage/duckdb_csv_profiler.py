"""DuckDB typed/raw profiler cho logical type inference."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

import duckdb
from src.application.data_sources.source_analysis_models import ProfiledTableSource
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.column_profile import ColumnProfile
from src.infrastructure.storage.duckdb_csv_reader import AUTO_TYPE_CANDIDATES, quote_identifier

RAW_TABLE: Final = "raw_csv"
MAX_DISTINCT_VALUES: Final = 20
MAX_SAMPLE_VALUES: Final = 10
DATE_FORMATS: Final = "['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']"
DATETIME_FORMATS: Final = "['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S']"


@dataclass(frozen=True, slots=True)
class _ColumnProfileInput:
    name: str
    physical_type: str
    total_rows: int


class DuckDbCsvProfiler:
    """Profile CSV bằng DuckDB nhưng bảo toàn raw string như leading zero."""

    def profile(self, file_bytes: bytes, filename: str) -> ProfiledTableSource:
        """Trả profile cột và dịch lỗi DuckDB/filesystem."""
        try:
            with TemporaryDirectory(prefix="p102_csv_profile_") as directory:
                path = Path(directory) / f"source{Path(filename).suffix.lower()}"
                path.write_bytes(file_bytes)
                return _profile_path(path, filename)
        except (duckdb.Error, OSError) as exc:
            raise InfrastructureException(
                ErrorCode.FILE_PARSING_ERROR,
                f"Không thể profile tệp CSV: {filename}",
            ) from exc


def _profile_path(path: Path, filename: str) -> ProfiledTableSource:
    with duckdb.connect() as connection:
        options = {"delimiter": "\t"} if path.suffix.lower() == ".tsv" else {}
        typed = connection.read_csv(
            str(path), auto_type_candidates=list(AUTO_TYPE_CANDIDATES), **options
        )
        raw = connection.read_csv(str(path), all_varchar=True, **options)
        raw.create(RAW_TABLE)
        total_rows = int(connection.execute(f"SELECT count(*) FROM {RAW_TABLE}").fetchone()[0])
        columns = tuple(
            _profile_column(connection, _ColumnProfileInput(name, str(type_name), total_rows))
            for name, type_name in zip(typed.columns, typed.types, strict=True)
        )
    return ProfiledTableSource(_table_name(filename), columns)


def _profile_column(
    connection: duckdb.DuckDBPyConnection,
    data: _ColumnProfileInput,
) -> ColumnProfile:
    identifier = quote_identifier(data.name)
    stats = connection.execute(_stats_sql(identifier)).fetchone()
    distinct_values = _distinct_values(connection, identifier)
    non_null_count = data.total_rows - int(stats[0])
    return ColumnProfile(
        name=data.name,
        physical_type=data.physical_type,
        sample_values=distinct_values[:MAX_SAMPLE_VALUES],
        distinct_values=distinct_values,
        null_count=int(stats[0]),
        distinct_count=int(stats[1]),
        total_rows=data.total_rows,
        average_length=float(stats[2]),
        is_fixed_length=non_null_count > 0 and int(stats[3]) == int(stats[4]),
        has_leading_zero=bool(stats[5]),
        date_match_ratio=_ratio(stats[6], non_null_count),
        datetime_match_ratio=_ratio(stats[7], non_null_count),
        top_value_ratio=_top_value_ratio(connection, identifier, non_null_count),
    )


def _stats_sql(identifier: str) -> str:
    return f"""
        SELECT count(*) - count({identifier}), count(DISTINCT {identifier}),
               coalesce(avg(length({identifier})), 0),
               coalesce(min(length({identifier})), 0),
               coalesce(max(length({identifier})), 0),
               count(*) FILTER (WHERE regexp_matches({identifier}, '^0[0-9]+$')),
               count(try_strptime({identifier}, {DATE_FORMATS})),
               count(try_strptime({identifier}, {DATETIME_FORMATS}))
        FROM {RAW_TABLE}
    """


def _distinct_values(
    connection: duckdb.DuckDBPyConnection,
    identifier: str,
) -> tuple[str, ...]:
    rows = connection.execute(
        f"SELECT {identifier} FROM {RAW_TABLE} WHERE {identifier} IS NOT NULL "
        f"GROUP BY {identifier} ORDER BY min(rowid) LIMIT ?",
        [MAX_DISTINCT_VALUES],
    ).fetchall()
    return tuple(str(row[0]) for row in rows)


def _top_value_ratio(
    connection: duckdb.DuckDBPyConnection,
    identifier: str,
    non_null_count: int,
) -> float:
    if not non_null_count:
        return 0
    count = connection.execute(
        f"SELECT coalesce(max(frequency), 0) FROM "
        f"(SELECT count(*) AS frequency FROM {RAW_TABLE} "
        f"WHERE {identifier} IS NOT NULL GROUP BY {identifier})"
    ).fetchone()[0]
    return int(count) / non_null_count


def _ratio(count: object, total: int) -> float:
    return int(count) / total if total else 0


def _table_name(filename: str) -> str:
    return filename.rsplit(".", 1)[0] or "Table1"
