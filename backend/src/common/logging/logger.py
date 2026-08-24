"""API lấy logger chuẩn hóa cho các tầng Clean Architecture (logger.py)."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Trả về một Logger instance chuẩn hóa dựa trên name (thường truyền __name__).

    Ví dụ sử dụng:
        from src.common.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Application event started")
    """
    return logging.getLogger(name)
