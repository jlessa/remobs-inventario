from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.inventory import InventoryItem
from app.models.sync import SyncAction
from app.schemas.sync import (
    SyncConflictDecision,
    SyncConflictDecisionRead,
    SyncConflictListRead,
    SyncPullRead,
    SyncPushRead,
    SyncPushRequest,
    SyncStatusRead,
)
from app.services.audit_service import log_action
from app.services.inventory_service import serialize_item

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/push", response_model=SyncPushRead)
async def push_sync_actions(
    payload: SyncPushRequest,
    user: AuthUser = Depends(require_permissions(["sync:write"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    accepted: list[str] = []
    for action in payload.actions:
        entry = SyncAction(
            client_action_id=action.client_action_id,
            action_type=action.action_type,
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            payload=action.payload,
            user_id=user.id,
            username=user.username,
            status="accepted",
        )
        session.add(entry)
        accepted.append(action.client_action_id)
        await log_action(
            session,
            actor=user,
            action="offline_action_accepted",
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            source="offline_sync",
            metadata={"client_action_id": action.client_action_id, "action_type": action.action_type},
        )
    await session.commit()
    return {"accepted_actions": accepted, "rejected_actions": []}


@router.get("/pull", response_model=SyncPullRead)
async def pull_changes(
    since: datetime | None = Query(default=None),
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    stmt = select(InventoryItem).where(InventoryItem.deleted_at.is_(None))
    if since:
        stmt = stmt.where(InventoryItem.updated_at >= since)
    items = (await session.execute(stmt.order_by(InventoryItem.updated_at))).scalars().all()
    return {
        "server_time": datetime.now(timezone.utc),
        "changes": {"inventory_items": [await serialize_item(session, item) for item in items]},
    }


@router.get("/status", response_model=SyncStatusRead)
async def sync_status(
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    pending = (
        await session.execute(
            select(SyncAction).where(SyncAction.user_id == user.id, SyncAction.status == "pending")
        )
    ).scalars().all()
    conflicts = (
        await session.execute(
            select(SyncAction).where(SyncAction.user_id == user.id, SyncAction.status == "conflict")
        )
    ).scalars().all()
    return {
        "pending_actions": len(pending),
        "conflict_actions": len(conflicts),
        "server_time": datetime.now(timezone.utc),
    }


@router.get("/conflicts", response_model=SyncConflictListRead)
async def list_conflicts(
    user: AuthUser = Depends(require_permissions(["sync:write"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    items = (
        await session.execute(
            select(SyncAction)
            .where(SyncAction.user_id == user.id, SyncAction.status == "conflict")
            .order_by(SyncAction.created_at.desc())
        )
    ).scalars().all()
    return {
        "items": [
            {
                "id": str(item.id),
                "client_action_id": item.client_action_id,
                "action_type": item.action_type,
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "payload": item.payload,
                "status": item.status,
                "error_message": item.error_message,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "total": len(items),
    }


@router.post("/resolve-conflict", response_model=SyncConflictDecisionRead)
async def resolve_conflict(
    payload: SyncConflictDecision,
    user: AuthUser = Depends(require_permissions(["sync:write"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    action = await session.scalar(
        select(SyncAction).where(
            SyncAction.client_action_id == payload.client_action_id,
            SyncAction.user_id == user.id,
            SyncAction.status == "conflict",
        )
    )
    if not action:
        return {"status": "not_found", "client_action_id": payload.client_action_id}

    status_by_decision = {
        "adjust": "adjusted",
        "discard": "discarded",
        "send_to_admin": "sent_to_admin",
    }
    before_payload = dict(action.payload)
    action.status = status_by_decision[payload.decision]
    if payload.adjusted_payload is not None:
        action.payload = {**action.payload, "adjusted_payload": payload.adjusted_payload}

    await log_action(
        session,
        actor=user,
        action="offline_conflict_resolved",
        entity_type="sync",
        entity_id=str(action.id),
        source="offline_sync",
        before_data={"status": "conflict", "payload": before_payload},
        after_data={"status": action.status, "decision": payload.decision},
        reason=payload.reason,
    )
    await session.commit()
    return {"status": action.status, "client_action_id": action.client_action_id}
