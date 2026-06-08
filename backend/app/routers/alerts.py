from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.alert import Alert
from app.schemas.alert import AlertListRead

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListRead)
async def list_alerts(
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    items = (await session.execute(select(Alert).order_by(Alert.created_at.desc()))).scalars().all()
    return {"items": items, "total": len(items)}
