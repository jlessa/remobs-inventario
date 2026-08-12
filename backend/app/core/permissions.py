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


def has_any_permission(user_permissions: Iterable[str], alternatives: Iterable[str]) -> bool:
    permissions = set(user_permissions)
    if "*" in permissions:
        return True
    return any(permission in permissions for permission in alternatives)


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


def require_any_permission(alternatives: Iterable[str]) -> Callable[..., AuthUser]:
    """Exige ao menos uma das permissões (útil para compatibilidade com códigos legados)."""
    allowed = list(alternatives)

    async def dependency(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if has_any_permission(user.permissions, allowed):
            return user
        raise AppError(
            "Permissões insuficientes.",
            code="permissions_missing",
            status_code=403,
            meta={"missing_permissions": allowed},
        )

    return dependency
