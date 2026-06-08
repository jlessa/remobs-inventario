from __future__ import annotations

from collections.abc import Iterable
from typing import Callable

from fastapi import Depends

from app.core.errors import AppError
from app.core.security import AuthUser, get_current_user


def missing_permissions(user_permissions: Iterable[str], required_permissions: Iterable[str]) -> list[str]:
    permissions = set(user_permissions)
    if "*" in permissions:
        return []
    return [permission for permission in required_permissions if permission not in permissions]


def require_permissions(required_permissions: Iterable[str]) -> Callable[..., AuthUser]:
    required = list(required_permissions)

    async def dependency(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        missing = missing_permissions(user.permissions, required)
        if missing:
            raise AppError(
                "Permissões insuficientes.",
                code="permissions_missing",
                status_code=403,
                meta={"missing_permissions": missing},
            )
        return user

    return dependency
