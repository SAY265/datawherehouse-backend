"""Mã hóa thông tin xác thực Sandbox trước khi lưu CSDL."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

TOKEN_PREFIX = "fernet:"


class CredentialCipher:
    """Fernet cipher dùng khóa dẫn xuất từ application secret."""

    def __init__(self, secret_key: str) -> None:
        digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(digest))

    def encrypt(self, value: str | None) -> str | None:
        """Mã hóa credential; không tạo token cho giá trị thiếu."""
        if value is None:
            return None
        token = self._fernet.encrypt(value.encode("utf-8")).decode("ascii")
        return f"{TOKEN_PREFIX}{token}"

    def decrypt(self, value: str | None) -> str | None:
        """Giải mã token và tương thích dữ liệu plaintext cũ để có thể migrate dần."""
        if value is None or not value.startswith(TOKEN_PREFIX):
            return value
        try:
            token = value.removeprefix(TOKEN_PREFIX).encode("ascii")
            return self._fernet.decrypt(token).decode("utf-8")
        except (InvalidToken, UnicodeError, ValueError) as exc:
            raise ValueError("Không thể giải mã Sandbox credential.") from exc
