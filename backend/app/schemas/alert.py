from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AlertRead(BaseModel):
    id: uuid.UUID
    alert_type: str
    severity: str
    entity_type: str
    entity_id: str
    title: str
    message: str
    status: str
    assigned_to: int | None
    created_at: datetime
    resolved_at: datetime | None
    alert_metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class AlertListRead(BaseModel):
    items: list[AlertRead]
    total: int
