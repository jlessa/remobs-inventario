from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.schemas.alert import AlertRead


class DashboardCriticalStockItemRead(BaseModel):
    id: uuid.UUID
    name: str
    unit: str
    stock_total: int
    minimum_stock_national: int


class DashboardSummaryRead(BaseModel):
    items_registered: int
    critical_stock: int
    pending_requests: int
    platforms_in_operation: int
    platforms_in_maintenance: int
    sensors_with_alert: int
    checklists_registered: int
    checklists_submitted: int
    offline_pending: int
    offline_conflicts: int
    critical_alerts: list[AlertRead]
    critical_stock_items: list[DashboardCriticalStockItemRead]
