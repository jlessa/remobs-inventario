from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.errors import AppError
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.inventory import StockMovement
from app.schemas.inventory import MovementDecision, MovementListRead, MovementRequestCreate, StockMovementRead
from app.services.audit_service import log_action
from app.services.inventory_service import (
    ensure_stock_alert,
    get_balance,
    get_item_or_404,
    get_or_create_balance,
    get_or_create_location,
    serialize_movement,
)

router = APIRouter(prefix="/inventory/movements", tags=["movements"])


@router.get("", response_model=MovementListRead)
async def list_movements(
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    movements = (
        await session.execute(select(StockMovement).order_by(StockMovement.created_at.desc()))
    ).scalars().all()
    return {"items": [await serialize_movement(session, movement) for movement in movements], "total": len(movements)}


@router.post("/request", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
async def request_movement(
    payload: MovementRequestCreate,
    user: AuthUser = Depends(require_permissions(["inventory:movement:request"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    item = await get_item_or_404(session, payload.item_id)
    from_balance = await get_balance(session, item_id=item.id, location_id=payload.from_location_id)
    if not from_balance or from_balance.quantity < payload.quantity:
        raise AppError("Estoque insuficiente para esta saída.", code="stock_insufficient", status_code=409)

    to_location = await get_or_create_location(session, location_id=payload.to_location_id, name=payload.to_location_name)
    movement = StockMovement(
        item_id=item.id,
        movement_type="saida",
        from_location_id=payload.from_location_id,
        to_location_id=to_location.id,
        quantity=payload.quantity,
        requested_by_id=user.id,
        requested_by_username=user.username,
        status="pending",
        reason=payload.reason,
    )
    session.add(movement)
    await session.flush()
    await log_action(
        session,
        actor=user,
        action="stock_movement_requested",
        entity_type="stock_movement",
        entity_id=str(movement.id),
        entity_label_snapshot=item.name,
        after_data=await serialize_movement(session, movement),
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(movement)
    return await serialize_movement(session, movement)


@router.post("/{movement_id}/approve", response_model=StockMovementRead)
async def approve_movement(
    movement_id: uuid.UUID,
    payload: MovementDecision,
    user: AuthUser = Depends(require_permissions(["inventory:movement:approve"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    movement = await session.get(StockMovement, movement_id)
    if not movement:
        raise AppError("Movimentação não encontrada.", code="movement_not_found", status_code=404)
    if movement.status != "pending":
        raise AppError("Movimentação não está pendente.", code="movement_not_pending", status_code=409)
    if movement.requested_by_id == user.id and "*" not in user.permissions:
        raise AppError("Solicitante não pode aprovar a própria saída.", code="self_approval_denied", status_code=403)

    item = await get_item_or_404(session, movement.item_id)
    from_balance = await get_balance(session, item_id=item.id, location_id=movement.from_location_id)
    if not from_balance or from_balance.quantity < movement.quantity:
        raise AppError("Estoque insuficiente para aprovar esta saída.", code="stock_insufficient", status_code=409)

    to_balance = await get_or_create_balance(session, item_id=item.id, location_id=movement.to_location_id)
    before_data = await serialize_movement(session, movement)
    from_balance.quantity -= movement.quantity
    to_balance.quantity += movement.quantity
    movement.status = "approved"
    movement.approved_by_id = user.id
    movement.approved_by_username = user.username
    movement.approved_at = datetime.now(timezone.utc)
    movement.completed_at = movement.approved_at
    movement.decision_reason = payload.reason
    item.current_location_id = movement.to_location_id
    item.row_version += 1

    await log_action(
        session,
        actor=user,
        action="stock_movement_approved",
        entity_type="stock_movement",
        entity_id=str(movement.id),
        entity_label_snapshot=item.name,
        before_data=before_data,
        after_data=await serialize_movement(session, movement),
        reason=payload.reason,
    )
    await ensure_stock_alert(session, item)
    await session.commit()
    await session.refresh(movement)
    return await serialize_movement(session, movement)


@router.post("/{movement_id}/reject", response_model=StockMovementRead)
async def reject_movement(
    movement_id: uuid.UUID,
    payload: MovementDecision,
    user: AuthUser = Depends(require_permissions(["inventory:movement:approve"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    movement = await session.get(StockMovement, movement_id)
    if not movement:
        raise AppError("Movimentação não encontrada.", code="movement_not_found", status_code=404)
    if movement.status != "pending":
        raise AppError("Movimentação não está pendente.", code="movement_not_pending", status_code=409)

    before_data = await serialize_movement(session, movement)
    movement.status = "rejected"
    movement.approved_by_id = user.id
    movement.approved_by_username = user.username
    movement.approved_at = datetime.now(timezone.utc)
    movement.decision_reason = payload.reason
    await log_action(
        session,
        actor=user,
        action="stock_movement_rejected",
        entity_type="stock_movement",
        entity_id=str(movement.id),
        before_data=before_data,
        after_data=await serialize_movement(session, movement),
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(movement)
    return await serialize_movement(session, movement)
