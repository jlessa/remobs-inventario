from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.errors import AppError
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.platform import Platform
from app.models.sensor import Sensor, SensorInstallation
from app.schemas.sensor import SensorCreate, SensorDetailRead, SensorListRead, SensorRead, SensorUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("", response_model=SensorListRead)
async def list_sensors(
    user: AuthUser = Depends(require_permissions(["sensor:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    items = (
        await session.execute(select(Sensor).where(Sensor.deleted_at.is_(None)).order_by(Sensor.family, Sensor.model))
    ).scalars().all()
    return {"items": items, "total": len(items)}


@router.post("", response_model=SensorRead, status_code=status.HTTP_201_CREATED)
async def create_sensor(
    payload: SensorCreate,
    user: AuthUser = Depends(require_permissions(["sensor:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Sensor:
    sensor = Sensor(**payload.model_dump())
    session.add(sensor)
    await session.flush()
    await log_action(
        session,
        actor=user,
        action="sensor_created",
        entity_type="sensor",
        entity_id=str(sensor.id),
        entity_label_snapshot=sensor.family,
        after_data=payload.model_dump(mode="json"),
    )
    await session.commit()
    await session.refresh(sensor)
    return sensor


@router.get("/{sensor_id}", response_model=SensorDetailRead)
async def get_sensor(
    sensor_id: uuid.UUID,
    user: AuthUser = Depends(require_permissions(["sensor:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    sensor = await session.get(Sensor, sensor_id)
    if not sensor or sensor.deleted_at is not None:
        raise AppError("Sensor não encontrado.", code="sensor_not_found", status_code=404)

    installation_rows = (
        await session.execute(
            select(SensorInstallation, Platform)
            .join(Platform, Platform.id == SensorInstallation.platform_id)
            .where(SensorInstallation.sensor_id == sensor.id)
            .order_by(SensorInstallation.installed_at.desc().nullslast(), Platform.name)
        )
    ).all()
    current_platform = next(
        (
            {
                "id": platform.id,
                "name": platform.name,
                "platform_type": platform.platform_type,
                "operational_status": platform.operational_status,
            }
            for installation, platform in installation_rows
            if installation.status == "ativo"
        ),
        None,
    )

    return {
        "id": sensor.id,
        "sensor_type": sensor.sensor_type,
        "family": sensor.family,
        "brand": sensor.brand,
        "model": sensor.model,
        "serial_number": sensor.serial_number,
        "patrimony_number": sensor.patrimony_number,
        "operational_status": sensor.operational_status,
        "calibration_due_at": sensor.calibration_due_at,
        "notes": sensor.notes,
        "created_at": sensor.created_at,
        "updated_at": sensor.updated_at,
        "current_platform": current_platform,
        "installations": [
            {
                "id": installation.id,
                "platform_id": platform.id,
                "platform_name": platform.name,
                "status": installation.status,
                "installed_at": installation.installed_at,
                "removed_at": installation.removed_at,
                "notes": installation.notes,
            }
            for installation, platform in installation_rows
        ],
    }


@router.patch("/{sensor_id}", response_model=SensorRead)
async def update_sensor(
    sensor_id: uuid.UUID,
    payload: SensorUpdate,
    user: AuthUser = Depends(require_permissions(["sensor:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> Sensor:
    sensor = await session.get(Sensor, sensor_id)
    if not sensor or sensor.deleted_at is not None:
        raise AppError("Sensor não encontrado.", code="sensor_not_found", status_code=404)

    before = {
        "family": sensor.family,
        "model": sensor.model,
        "operational_status": sensor.operational_status,
    }
    for field, value in payload.model_dump(exclude_unset=True, exclude={"reason"}).items():
        setattr(sensor, field, value)
    await log_action(
        session,
        actor=user,
        action="sensor_updated",
        entity_type="sensor",
        entity_id=str(sensor.id),
        entity_label_snapshot=sensor.family,
        before_data=before,
        after_data=payload.model_dump(mode="json", exclude_none=True),
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(sensor)
    return sensor
