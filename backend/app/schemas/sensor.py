from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SensorCreate(BaseModel):
    sensor_type: str
    family: str = Field(min_length=1, max_length=120)
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    patrimony_number: str | None = None
    operational_status: str = "nao_instalado"
    calibration_due_at: datetime | None = None
    notes: str | None = None


class SensorUpdate(BaseModel):
    sensor_type: str | None = None
    family: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    patrimony_number: str | None = None
    operational_status: str | None = None
    calibration_due_at: datetime | None = None
    notes: str | None = None
    reason: str | None = None


class SensorRead(BaseModel):
    id: uuid.UUID
    sensor_type: str
    family: str
    brand: str | None
    model: str | None
    serial_number: str | None
    patrimony_number: str | None
    operational_status: str
    calibration_due_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensorListRead(BaseModel):
    items: list[SensorRead]
    total: int


class SensorPlatformRead(BaseModel):
    id: uuid.UUID
    name: str
    platform_type: str
    operational_status: str


class SensorInstallationRead(BaseModel):
    id: uuid.UUID
    platform_id: uuid.UUID
    platform_name: str
    status: str
    installed_at: datetime | None
    removed_at: datetime | None
    notes: str | None


class SensorDetailRead(SensorRead):
    current_platform: SensorPlatformRead | None
    installations: list[SensorInstallationRead]
