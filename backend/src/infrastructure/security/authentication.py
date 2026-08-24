"""FastAPI HTTP Bearer scheme shared by authentication dependencies."""

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description="JWT access token returned by /api/v1/auth/login or /register.",
)

BearerCredentials = HTTPAuthorizationCredentials
