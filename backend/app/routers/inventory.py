from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.inventory import InventoryItem, StockBalance, StockMovement
from app.schemas.inventory import (
    InventoryDeleteRequest,
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    InventoryListRead,
    ItemHistoryRead,
)
from app.services.audit_service import log_action
from app.services.inventory_service import (
    active_items_query,
    audit_logs_for_item,
    ensure_stock_alert,
    get_item_or_404,
    get_or_create_balance,
    get_or_create_category,
    get_or_create_location,
    serialize_item,
    serialize_movement,
)

router = APIRouter(prefix="/inventory/items", tags=["inventory"])


@router.get("", response_model=InventoryListRead)
async def list_items(
    q: str | None = Query(default=None),
    item_type: str | None = Query(default=None),
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    stmt = active_items_query().order_by(InventoryItem.name)
    if q:
        stmt = stmt.where(InventoryItem.name.ilike(f"%{q}%"))
    if item_type:
        stmt = stmt.where(InventoryItem.item_type == item_type)

    items = (await session.execute(stmt)).scalars().all()
    return {"items": [await serialize_item(session, item) for item in items], "total": len(items)}


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: InventoryItemCreate,
    user: AuthUser = Depends(require_permissions(["inventory:item:create"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    category = await get_or_create_category(session, category_id=payload.category_id, name=payload.category_name)
    location = await get_or_create_location(session, location_id=payload.current_location_id, name=payload.location_name)
    item = InventoryItem(
        item_type=payload.item_type,
        category_id=category.id,
        name=payload.name,
        brand=payload.brand,
        model=payload.model,
        serial_number=payload.serial_number,
        patrimony_number=payload.patrimony_number,
        invoice_number=payload.invoice_number,
        description=payload.description,
        condition_status=payload.condition_status,
        current_location_id=location.id,
        unit=payload.unit,
        minimum_stock_national=payload.minimum_stock_national,
        minimum_stock_import=payload.minimum_stock_import,
        minimum_stock_maintenance=payload.minimum_stock_maintenance,
        ideal_stock=payload.ideal_stock,
    )
    session.add(item)
    await session.flush()

    if payload.initial_quantity:
        balance = await get_or_create_balance(session, item_id=item.id, location_id=location.id)
        balance.quantity += payload.initial_quantity

    after_data = await serialize_item(session, item)
    await log_action(
        session,
        actor=user,
        action="inventory_item_created",
        entity_type="inventory_item",
        entity_id=str(item.id),
        entity_label_snapshot=item.name,
        after_data=after_data,
        reason=payload.reason,
    )
    await ensure_stock_alert(session, item)
    await session.commit()
    await session.refresh(item)
    return await serialize_item(session, item)


@router.get("/{item_id}", response_model=InventoryItemRead)
async def get_item(
    item_id: uuid.UUID,
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    item = await get_item_or_404(session, item_id)
    return await serialize_item(session, item)


@router.patch("/{item_id}", response_model=InventoryItemRead)
async def update_item(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    user: AuthUser = Depends(require_permissions(["inventory:item:update"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    item = await get_item_or_404(session, item_id)
    before_data = await serialize_item(session, item)
    data = payload.model_dump(exclude_unset=True)

    if "category_name" in data or "category_id" in data:
        category = await get_or_create_category(session, category_id=payload.category_id, name=payload.category_name)
        item.category_id = category.id
    if "location_name" in data or "current_location_id" in data:
        location = await get_or_create_location(session, location_id=payload.current_location_id, name=payload.location_name)
        item.current_location_id = location.id

    ignored = {"category_name", "category_id", "location_name", "current_location_id", "reason"}
    for field, value in data.items():
        if field not in ignored:
            setattr(item, field, value)
    item.row_version += 1

    after_data = await serialize_item(session, item)
    await log_action(
        session,
        actor=user,
        action="inventory_item_updated",
        entity_type="inventory_item",
        entity_id=str(item.id),
        entity_label_snapshot=item.name,
        before_data=before_data,
        after_data=after_data,
        reason=payload.reason,
    )
    await ensure_stock_alert(session, item)
    await session.commit()
    await session.refresh(item)
    return await serialize_item(session, item)


@router.delete("/{item_id}")
async def delete_item(
    item_id: uuid.UUID,
    payload: InventoryDeleteRequest,
    user: AuthUser = Depends(require_permissions(["inventory:item:delete"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    item = await get_item_or_404(session, item_id)
    before_data = await serialize_item(session, item)
    item.is_active = False
    item.deleted_at = datetime.now(timezone.utc)
    item.row_version += 1
    await log_action(
        session,
        actor=user,
        action="inventory_item_deleted",
        entity_type="inventory_item",
        entity_id=str(item.id),
        entity_label_snapshot=item.name,
        before_data=before_data,
        after_data={"deleted_at": item.deleted_at.isoformat(), "is_active": False},
        reason=payload.reason,
    )
    await session.commit()
    return {"status": "ok"}


@router.get("/{item_id}/history", response_model=ItemHistoryRead)
async def get_item_history(
    item_id: uuid.UUID,
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await get_item_or_404(session, item_id)
    movements = (
        await session.execute(
            select(StockMovement)
            .where(StockMovement.item_id == item_id)
            .order_by(StockMovement.created_at.desc())
        )
    ).scalars().all()
    return {
        "movements": [await serialize_movement(session, movement) for movement in movements],
        "audit_logs": await audit_logs_for_item(session, item_id),
    }
