from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    location_type: str = Field(default="estoque", min_length=1, max_length=64)


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    location_type: str | None = Field(default=None, min_length=1, max_length=64)
    is_active: bool | None = None
    reason: str | None = None


class LocationDeleteRequest(BaseModel):
    reason: str = Field(min_length=3)


class LocationRead(BaseModel):
    id: uuid.UUID
    name: str
    location_type: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationListRead(BaseModel):
    items: list[LocationRead]
    total: int
