from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntityFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_id: uuid.UUID
    entity_type: str
    entity_id: str
    file_role: str
    notes: str | None
    original_name: str
    mime_type: str
    size_bytes: int
    uploaded_by: int
    created_at: datetime
    download_path: str


class EntityFileListRead(BaseModel):
    items: list[EntityFileRead]
    total: int


class EntityFileDeleteRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)
