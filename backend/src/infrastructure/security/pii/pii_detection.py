"""Model nội bộ mô tả một vùng PII đã được phát hiện."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PiiDetection:
    """Kết quả detect độc lập với model public của Presidio."""

    entity_type: str
    start: int
    end: int
    score: float
