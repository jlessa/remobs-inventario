from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.errors import AppError
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.platform import Hull, Platform, PlatformSystem
from app.models.sensor import Sensor, SensorInstallation
from app.schemas.platform import PlatformCreate, PlatformDetailRead, PlatformListRead, PlatformRead, PlatformUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("", response_model=PlatformListRead)
async def list_platforms(
    user: AuthUser = Depends(require_permissions(["platform:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    items = (
        await session.execute(select(Platform).where(Platform.deleted_at.is_(None)).order_by(Platform.name))
    ).scalars().all()
    return {"items": items, "total": len(items)}


@router.post("", response_model=PlatformRead, status_code=status.HTTP_201_CREATED)
async def create_platform(
    payload: PlatformCreate,
    user: AuthUser = Depends(require_permissions(["platform:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Platform:
    platform = Platform(**payload.model_dump())
    session.add(platform)
    await session.flush()
    await log_action(
        session,
        actor=user,
        action="platform_created",
        entity_type="platform",
        entity_id=str(platform.id),
        entity_label_snapshot=platform.name,
        after_data=payload.model_dump(),
    )
    await session.commit()
    await session.refresh(platform)
    return platform


@router.get("/{platform_id}", response_model=PlatformDetailRead)
async def get_platform(
    platform_id: uuid.UUID,
    user: AuthUser = Depends(require_permissions(["platform:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    platform = await session.get(Platform, platform_id)
    if not platform or platform.deleted_at is not None:
        raise AppError("Plataforma não encontrada.", code="platform_not_found", status_code=404)

    hull = await session.scalar(select(Hull).where(Hull.platform_id == platform.id).order_by(Hull.code))
    systems = (
        await session.execute(
            select(PlatformSystem).where(PlatformSystem.platform_id == platform.id).order_by(PlatformSystem.name)
        )
    ).scalars().all()
    sensor_rows = (
        await session.execute(
            select(Sensor, SensorInstallation)
            .join(SensorInstallation, SensorInstallation.sensor_id == Sensor.id)
            .where(
                SensorInstallation.platform_id == platform.id,
                SensorInstallation.status == "ativo",
                Sensor.deleted_at.is_(None),
            )
            .order_by(Sensor.family, Sensor.model)
        )
    ).all()

    return {
        "id": platform.id,
        "name": platform.name,
        "platform_type": platform.platform_type,
        "manufacturer": platform.manufacturer,
        "model": platform.model,
        "operational_status": platform.operational_status,
        "description": platform.description,
        "created_at": platform.created_at,
        "updated_at": platform.updated_at,
        "hull": hull,
        "systems": systems,
        "sensors": [
            {
                "id": sensor.id,
                "sensor_type": sensor.sensor_type,
                "family": sensor.family,
                "brand": sensor.brand,
                "model": sensor.model,
                "serial_number": sensor.serial_number,
                "operational_status": sensor.operational_status,
                "installation_status": installation.status,
                "installation_notes": installation.notes,
            }
            for sensor, installation in sensor_rows
        ],
    }


@router.patch("/{platform_id}", response_model=PlatformRead)
async def update_platform(
    platform_id: uuid.UUID,
    payload: PlatformUpdate,
    user: AuthUser = Depends(require_permissions(["platform:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Platform:
    platform = await session.get(Platform, platform_id)
    if not platform or platform.deleted_at is not None:
        raise AppError("Plataforma não encontrada.", code="platform_not_found", status_code=404)

    before = {
        "name": platform.name,
        "platform_type": platform.platform_type,
        "operational_status": platform.operational_status,
    }
    for field, value in payload.model_dump(exclude_unset=True, exclude={"reason"}).items():
        setattr(platform, field, value)
    await log_action(
        session,
        actor=user,
        action="platform_updated",
        entity_type="platform",
        entity_id=str(platform.id),
        entity_label_snapshot=platform.name,
        before_data=before,
        after_data=payload.model_dump(exclude_none=True),
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(platform)
    return platform
