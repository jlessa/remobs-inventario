from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.errors import AppError
from app.core.permissions import require_any_permission, require_permissions
from app.core.security import AuthUser
from app.models.inventory import Location
from app.schemas.location import (
    LocationCreate,
    LocationDeleteRequest,
    LocationListRead,
    LocationRead,
    LocationUpdate,
)
from app.services.audit_service import log_action

router = APIRouter(prefix="/locations", tags=["locations"])


async def _get_location_or_404(session: AsyncSession, location_id: uuid.UUID) -> Location:
    location = await session.get(Location, location_id)
    if not location:
        raise AppError("Local não encontrado.", code="location_not_found", status_code=404)
    return location


async def _ensure_unique_name(
    session: AsyncSession,
    *,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> None:
    stmt = select(Location).where(func.lower(Location.name) == name.strip().lower())
    if exclude_id is not None:
        stmt = stmt.where(Location.id != exclude_id)
    existing = await session.scalar(stmt)
    if existing:
        raise AppError("Já existe um local com este nome.", code="location_name_conflict", status_code=409)


@router.get("", response_model=LocationListRead)
async def list_locations(
    q: str | None = Query(None, description="Filtro por prefixo do nome (case-insensitive)."),
    active_only: bool = Query(True, description="Quando true, retorna apenas locais ativos."),
    user: AuthUser = Depends(
        require_any_permission(["location:read", "inventory:item:read", "inventory:movement:request"])
    ),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    stmt = select(Location)
    if active_only:
        stmt = stmt.where(Location.is_active.is_(True))
    if q and q.strip():
        stmt = stmt.where(Location.name.ilike(f"{q.strip()}%"))
    items = (await session.execute(stmt.order_by(Location.name))).scalars().all()
    return {"items": items, "total": len(items)}


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    user: AuthUser = Depends(require_any_permission(["location:create", "location:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Location:
    name = payload.name.strip()
    await _ensure_unique_name(session, name=name)
    location = Location(name=name, location_type=payload.location_type.strip() or "estoque")
    session.add(location)
    await session.flush()
    await log_action(
        session,
        actor=user,
        action="location_created",
        entity_type="location",
        entity_id=str(location.id),
        entity_label_snapshot=location.name,
        after_data={"name": location.name, "location_type": location.location_type},
    )
    await session.commit()
    await session.refresh(location)
    return location


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: uuid.UUID,
    user: AuthUser = Depends(
        require_any_permission(["location:read", "inventory:item:read", "inventory:movement:request"])
    ),
    session: AsyncSession = Depends(get_async_session),
) -> Location:
    return await _get_location_or_404(session, location_id)


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdate,
    user: AuthUser = Depends(require_permissions(["location:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Location:
    location = await _get_location_or_404(session, location_id)
    before = {
        "name": location.name,
        "location_type": location.location_type,
        "is_active": location.is_active,
    }
    data = payload.model_dump(exclude_unset=True, exclude={"reason"})
    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        await _ensure_unique_name(session, name=name, exclude_id=location.id)
        location.name = name
    if "location_type" in data and data["location_type"] is not None:
        location.location_type = data["location_type"].strip() or location.location_type
    if "is_active" in data and data["is_active"] is not None:
        location.is_active = data["is_active"]

    await log_action(
        session,
        actor=user,
        action="location_updated",
        entity_type="location",
        entity_id=str(location.id),
        entity_label_snapshot=location.name,
        before_data=before,
        after_data=payload.model_dump(exclude_none=True),
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(location)
    return location


@router.delete("/{location_id}")
async def delete_location(
    location_id: uuid.UUID,
    payload: LocationDeleteRequest,
    user: AuthUser = Depends(require_any_permission(["location:delete", "location:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    location = await _get_location_or_404(session, location_id)
    if not location.is_active:
        raise AppError("Local já está inativo.", code="location_already_inactive", status_code=409)

    before = {
        "name": location.name,
        "location_type": location.location_type,
        "is_active": location.is_active,
    }
    location.is_active = False
    await log_action(
        session,
        actor=user,
        action="location_deleted",
        entity_type="location",
        entity_id=str(location.id),
        entity_label_snapshot=location.name,
        before_data=before,
        after_data={"is_active": False},
        reason=payload.reason,
    )
    await session.commit()
    return {"status": "ok"}
