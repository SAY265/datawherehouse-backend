"""Value objects cho miền Người dùng (User)."""

import re
from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.value_object import BaseValueObject

# Regex kiểm tra định dạng email hợp lệ:
# - ^[^@\s]+: Tên email (local part) gồm 1+ ký tự không chứa '@' hoặc khoảng trắng.
# - @: Ký tự '@' bắt buộc.
# - [^@\s.]+: Tên miền chính (domain name) không chứa '@', khoảng trắng hay dấu '.'.
# - (\.[^@\s.]+)+: Phần tên miền mở rộng (TLD/subdomain như .com, .vn, .edu.vn), bắt đầu bằng '.'
#   ngăn ngừa các dấu chấm liên tiếp ('..') hoặc chấm ở cuối.
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


@dataclass(frozen=True)
class Email(BaseValueObject):
    """Value Object đại diện cho địa chỉ Email hợp lệ."""

    value: str

    def __post_init__(self) -> None:
        """Kiểm tra định dạng email hợp lệ khi khởi tạo."""
        if not isinstance(self.value, str) or not self.value.strip():
            raise BusinessException(
                code=ErrorCode.INVALID_EMAIL,
                message="Địa chỉ email không được để trống.",
            )

        normalized = self.value.strip().lower()
        if not EMAIL_REGEX.match(normalized):
            raise BusinessException(
                code=ErrorCode.INVALID_EMAIL,
                message=f"Địa chỉ email '{self.value}' không đúng định dạng.",
            )

        object.__setattr__(self, "value", normalized)
