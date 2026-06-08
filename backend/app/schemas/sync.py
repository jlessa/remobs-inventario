from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SyncActionIn(BaseModel):
    client_action_id: str = Field(min_length=1)
    action_type: str
    entity_type: str
    entity_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class SyncPushRequest(BaseModel):
    actions: list[SyncActionIn] = Field(default_factory=list)


class SyncPushRead(BaseModel):
    accepted_actions: list[str]
    rejected_actions: list[dict[str, Any]]


class SyncPullRead(BaseModel):
    server_time: datetime
    changes: dict[str, list[dict[str, Any]]]


class SyncStatusRead(BaseModel):
    pending_actions: int
    conflict_actions: int = 0
    server_time: datetime


class SyncConflictRead(BaseModel):
    id: str
    client_action_id: str
    action_type: str
    entity_type: str
    entity_id: str | None
    payload: dict[str, Any]
    status: str
    error_message: str | None
    created_at: datetime


class SyncConflictListRead(BaseModel):
    items: list[SyncConflictRead]
    total: int


class SyncConflictDecision(BaseModel):
    client_action_id: str = Field(min_length=1)
    decision: str = Field(pattern="^(adjust|discard|send_to_admin)$")
    adjusted_payload: dict[str, Any] | None = None
    reason: str = Field(min_length=3)


class SyncConflictDecisionRead(BaseModel):
    status: str
    client_action_id: str
