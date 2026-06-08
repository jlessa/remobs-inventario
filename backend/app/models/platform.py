from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.core.database import Base, table_ref


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    platform_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(160), nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    operational_status: Mapped[str] = mapped_column(String(80), default="disponivel", nullable=False, index=True)
    current_location_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey(table_ref("locations")), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Hull(Base):
    __tablename__ = "hulls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey(table_ref("platforms")), nullable=True)
    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="disponivel", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PlatformSystem(Base):
    __tablename__ = "platform_systems"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey(table_ref("platforms")), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), default="operacional", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SystemComponent(Base):
    __tablename__ = "system_components"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_system_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey(table_ref("platform_systems")), index=True)
    inventory_item_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey(table_ref("inventory_items")), index=True)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="instalado", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
