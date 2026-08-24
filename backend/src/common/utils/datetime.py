"""Utilities xử lý thời gian (datetime.py).

Tuân thủ nguyên tắc:
- Mọi thời gian hệ thống được xử lý theo UTC timezone-aware.
- Không sử dụng datetime.now() naive.
"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Trả về thời gian hiện tại chuẩn UTC timezone-aware."""
    return datetime.now(UTC)


def ensure_utc(dt: datetime) -> datetime:
    """Đảm bảo đối tượng datetime có timezone UTC.

    - Nếu naive (chưa có tzinfo): Gán tzinfo = timezone.utc.
    - Nếu đã có timezone khác: Chuyển đổi (astimezone) sang timezone.utc.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_isoformat(dt: datetime) -> str:
    """Chuyển đổi đối tượng datetime thành chuỗi chuẩn ISO 8601 UTC."""
    utc_dt = ensure_utc(dt)
    return utc_dt.isoformat()


def parse_iso_datetime(value: str) -> datetime:
    """Parse chuỗi ISO 8601 thành đối tượng datetime UTC timezone-aware.

    Ném ValueError nếu định dạng chuỗi không hợp lệ.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Gía trị datetime đầu vào phải là chuỗi không rỗng.")

    try:
        dt = datetime.fromisoformat(value.strip())
        return ensure_utc(dt)
    except ValueError as e:
        raise ValueError(f"Không thể parse ISO datetime từ chuỗi '{value}': {e}") from e
