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
from app.models.checklist import FieldChecklist
from app.schemas.checklist import ChecklistCreate, ChecklistListRead, ChecklistRead, ChecklistSubmit, ChecklistUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/checklists", tags=["checklists"])


async def get_checklist_or_404(session: AsyncSession, checklist_id: uuid.UUID) -> FieldChecklist:
    checklist = await session.get(FieldChecklist, checklist_id)
    if not checklist:
        raise AppError("Checklist não encontrado.", code="checklist_not_found", status_code=404)
    return checklist


@router.get("", response_model=ChecklistListRead)
async def list_checklists(
    user: AuthUser = Depends(require_permissions(["checklist:submit"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    items = (
        await session.execute(
            select(FieldChecklist).order_by(FieldChecklist.updated_at.desc(), FieldChecklist.created_at.desc())
        )
    ).scalars().all()
    return {"items": items, "total": len(items)}


@router.post("", response_model=ChecklistRead, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    payload: ChecklistCreate,
    user: AuthUser = Depends(require_permissions(["checklist:submit"])),
    session: AsyncSession = Depends(get_async_session),
) -> FieldChecklist:
    checklist = FieldChecklist(
        title=payload.title,
        template_name=payload.template_name,
        platform_id=payload.platform_id,
        platform_name=payload.platform_name,
        total_steps=payload.total_steps,
        answers=payload.answers,
        evidence=payload.evidence,
        submitted_by_id=user.id,
        submitted_by_username=user.username,
        notes=payload.notes,
    )
    session.add(checklist)
    await session.flush()
    await log_action(
        session,
        actor=user,
        action="field_checklist_draft_created",
        entity_type="field_checklist",
        entity_id=str(checklist.id),
        entity_label_snapshot=checklist.title,
        after_data=payload.model_dump(mode="json"),
    )
    await session.commit()
    await session.refresh(checklist)
    return checklist


@router.get("/{checklist_id}", response_model=ChecklistRead)
async def get_checklist(
    checklist_id: uuid.UUID,
    user: AuthUser = Depends(require_permissions(["checklist:submit"])),
    session: AsyncSession = Depends(get_async_session),
) -> FieldChecklist:
    return await get_checklist_or_404(session, checklist_id)


@router.patch("/{checklist_id}", response_model=ChecklistRead)
async def update_checklist(
    checklist_id: uuid.UUID,
    payload: ChecklistUpdate,
    user: AuthUser = Depends(require_permissions(["checklist:submit"])),
    session: AsyncSession = Depends(get_async_session),
) -> FieldChecklist:
    checklist = await get_checklist_or_404(session, checklist_id)
    if checklist.status == "submitted":
        raise AppError("Checklist enviado não pode ser editado.", code="checklist_already_submitted", status_code=409)

    before = {
        "status": checklist.status,
        "current_step": checklist.current_step,
        "answers": checklist.answers,
    }
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(checklist, field, value)

    await log_action(
        session,
        actor=user,
        action="field_checklist_draft_updated",
        entity_type="field_checklist",
        entity_id=str(checklist.id),
        entity_label_snapshot=checklist.title,
        before_data=before,
        after_data=payload.model_dump(mode="json", exclude_unset=True),
    )
    await session.commit()
    await session.refresh(checklist)
    return checklist


@router.post("/{checklist_id}/submit", response_model=ChecklistRead)
async def submit_checklist(
    checklist_id: uuid.UUID,
    payload: ChecklistSubmit,
    user: AuthUser = Depends(require_permissions(["checklist:submit"])),
    session: AsyncSession = Depends(get_async_session),
) -> FieldChecklist:
    checklist = await get_checklist_or_404(session, checklist_id)
    if checklist.status == "submitted":
        return checklist

    before = {"status": checklist.status, "current_step": checklist.current_step}
    checklist.status = "submitted"
    checklist.current_step = checklist.total_steps
    checklist.submitted_at = datetime.now(timezone.utc)

    await log_action(
        session,
        actor=user,
        action="field_checklist_submitted",
        entity_type="field_checklist",
        entity_id=str(checklist.id),
        entity_label_snapshot=checklist.title,
        before_data=before,
        after_data={"status": checklist.status, "submitted_at": checklist.submitted_at.isoformat()},
        reason=payload.reason,
    )
    await session.commit()
    await session.refresh(checklist)
    return checklist
