from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.errors import AppError


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    id: int
    username: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    resource_access: dict[str, Any] = field(default_factory=dict)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser:
    if credentials is None or not credentials.credentials:
        raise AppError(
            "Token de autenticação ausente.",
            code="not_authenticated",
            status_code=401,
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except jwt.ExpiredSignatureError as exc:
        raise AppError("Token expirado.", code="token_expired", status_code=401) from exc
    except jwt.InvalidAudienceError as exc:
        raise AppError("Audience do token inválida.", code="invalid_token_audience", status_code=401) from exc
    except jwt.InvalidIssuerError as exc:
        raise AppError("Issuer do token inválido.", code="invalid_token_issuer", status_code=401) from exc
    except jwt.PyJWTError as exc:
        raise AppError("Token inválido.", code="invalid_token", status_code=401) from exc

    subject = payload.get("sub")
    username = payload.get("username")
    if subject is None or username is None:
        raise AppError("Token sem identidade de usuário.", code="invalid_token_subject", status_code=401)

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise AppError("Identificador de usuário inválido.", code="invalid_token_subject", status_code=401) from exc

    permissions = payload.get("permissions") or []
    roles = payload.get("roles") or []
    if not isinstance(permissions, list) or not isinstance(roles, list):
        raise AppError("Claims de autorização inválidas.", code="invalid_token_claims", status_code=401)

    return AuthUser(
        id=user_id,
        username=str(username),
        roles=[str(role) for role in roles],
        permissions=[str(permission) for permission in permissions],
        resource_access=dict(payload.get("resource_access") or {}),
    )
