from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChecklistCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    template_name: str = Field(min_length=1, max_length=180)
    platform_id: uuid.UUID | None = None
    platform_name: str | None = None
    total_steps: int = Field(default=1, ge=1)
    answers: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    notes: str | None = None


class ChecklistUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    template_name: str | None = Field(default=None, min_length=1, max_length=180)
    platform_id: uuid.UUID | None = None
    platform_name: str | None = None
    status: str | None = None
    current_step: int | None = Field(default=None, ge=1)
    total_steps: int | None = Field(default=None, ge=1)
    answers: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] | None = None
    notes: str | None = None


class ChecklistSubmit(BaseModel):
    reason: str = Field(min_length=3)


class ChecklistRead(BaseModel):
    id: uuid.UUID
    title: str
    template_name: str
    platform_id: uuid.UUID | None
    platform_name: str | None
    status: str
    current_step: int
    total_steps: int
    answers: dict[str, Any]
    evidence: list[dict[str, Any]]
    submitted_by_id: int
    submitted_by_username: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ChecklistListRead(BaseModel):
    items: list[ChecklistRead]
    total: int
