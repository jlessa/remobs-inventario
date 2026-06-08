from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogListRead

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=AuditLogListRead)
async def list_audit_logs(
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    user: AuthUser = Depends(require_permissions(["audit:log:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    stmt = select(AuditLog).order_by(AuditLog.occurred_at.desc())
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)

    items = (await session.execute(stmt)).scalars().all()
    return {"items": items, "total": len(items)}
