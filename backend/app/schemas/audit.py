from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: uuid.UUID
    occurred_at: datetime
    actor_user_id: int | None
    actor_username: str | None
    actor_roles: list[str]
    action: str
    entity_type: str
    entity_id: str | None
    entity_label_snapshot: str | None
    before_data: dict[str, Any] | None
    after_data: dict[str, Any] | None
    diff: dict[str, Any] | None
    reason: str | None
    source: str
    status: str
    audit_metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class AuditLogListRead(BaseModel):
    items: list[AuditLogRead]
    total: int
