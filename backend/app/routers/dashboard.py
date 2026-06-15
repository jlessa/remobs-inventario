from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.permissions import require_permissions
from app.core.security import AuthUser
from app.models.alert import Alert
from app.models.checklist import FieldChecklist
from app.models.inventory import InventoryItem, StockBalance, StockMovement
from app.models.platform import Platform
from app.models.sensor import Sensor
from app.models.sync import SyncAction
from app.schemas.dashboard import DashboardSummaryRead

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def count_scalar(session: AsyncSession, statement) -> int:
    return int(await session.scalar(statement) or 0)


@router.get("/summary", response_model=DashboardSummaryRead)
async def dashboard_summary(
    user: AuthUser = Depends(require_permissions(["inventory:item:read"])),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    stock_totals = (
        select(
            StockBalance.item_id.label("item_id"),
            func.coalesce(func.sum(StockBalance.quantity), 0).label("stock_total"),
        )
        .group_by(StockBalance.item_id)
        .subquery()
    )
    stock_total = func.coalesce(stock_totals.c.stock_total, 0)
    active_item_filters = [InventoryItem.deleted_at.is_(None), InventoryItem.is_active.is_(True)]
    critical_stock_filters = [
        *active_item_filters,
        InventoryItem.minimum_stock_national > 0,
        stock_total < InventoryItem.minimum_stock_national,
    ]

    critical_stock_rows = (
        await session.execute(
            select(InventoryItem, stock_total.label("stock_total"))
            .outerjoin(stock_totals, stock_totals.c.item_id == InventoryItem.id)
            .where(*critical_stock_filters)
            .order_by((InventoryItem.minimum_stock_national - stock_total).desc(), InventoryItem.name)
            .limit(4)
        )
    ).all()
    critical_alerts = (
        await session.execute(
            select(Alert)
            .where(Alert.status == "open", Alert.severity.in_(["critical", "warning"]))
            .order_by(Alert.created_at.desc())
            .limit(4)
        )
    ).scalars().all()

    return {
        "items_registered": await count_scalar(
            session,
            select(func.count()).select_from(InventoryItem).where(*active_item_filters),
        ),
        "critical_stock": await count_scalar(
            session,
            select(func.count())
            .select_from(InventoryItem)
            .outerjoin(stock_totals, stock_totals.c.item_id == InventoryItem.id)
            .where(*critical_stock_filters),
        ),
        "pending_requests": await count_scalar(
            session,
            select(func.count()).select_from(StockMovement).where(StockMovement.status == "pending"),
        ),
        "platforms_in_operation": await count_scalar(
            session,
            select(func.count())
            .select_from(Platform)
            .where(Platform.deleted_at.is_(None), Platform.operational_status == "em_operacao"),
        ),
        "platforms_in_maintenance": await count_scalar(
            session,
            select(func.count())
            .select_from(Platform)
            .where(
                Platform.deleted_at.is_(None),
                Platform.operational_status.in_(["manutencao", "em_manutencao", "offline"]),
            ),
        ),
        "sensors_with_alert": await count_scalar(
            session,
            select(func.count())
            .select_from(Sensor)
            .where(Sensor.deleted_at.is_(None), Sensor.operational_status.in_(["avariado", "inconsistencia"])),
        ),
        "checklists_registered": await count_scalar(
            session,
            select(func.count()).select_from(FieldChecklist),
        ),
        "checklists_submitted": await count_scalar(
            session,
            select(func.count()).select_from(FieldChecklist).where(FieldChecklist.status == "submitted"),
        ),
        "offline_pending": await count_scalar(
            session,
            select(func.count())
            .select_from(SyncAction)
            .where(SyncAction.user_id == user.id, SyncAction.status == "pending"),
        ),
        "offline_conflicts": await count_scalar(
            session,
            select(func.count())
            .select_from(SyncAction)
            .where(SyncAction.user_id == user.id, SyncAction.status == "conflict"),
        ),
        "critical_alerts": critical_alerts,
        "critical_stock_items": [
            {
                "id": item.id,
                "name": item.name,
                "unit": item.unit,
                "stock_total": int(total or 0),
                "minimum_stock_national": item.minimum_stock_national,
            }
            for item, total in critical_stock_rows
        ],
    }
