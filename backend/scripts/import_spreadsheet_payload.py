from __future__ import annotations

import argparse
import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import AuthUser
from app.models.audit_log import AuditLog
from app.models.checklist import FieldChecklist
from app.models.inventory import InventoryCategory, InventoryItem, Location, StockBalance
from app.models.platform import Platform
from app.models.sensor import Sensor
from app.services.inventory_service import ensure_stock_alert


ACTOR = AuthUser(id=0, username="importacao-planilhas", roles=["system"], permissions=["*"])
MARKER_RE = re.compile(r"remobs-import:([0-9a-f]{16})")


def marker(source_key: str) -> str:
    return f"remobs-import:{source_key}"


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


async def get_or_create_category(session: AsyncSession, name: str) -> InventoryCategory:
    category = await session.scalar(select(InventoryCategory).where(func.lower(InventoryCategory.name) == name.lower()))
    if category:
        return category
    category = InventoryCategory(name=name)
    session.add(category)
    await session.flush()
    return category


async def get_or_create_location(session: AsyncSession, name: str) -> Location:
    location = await session.scalar(select(Location).where(func.lower(Location.name) == name.lower()))
    if location:
        return location
    location = Location(name=name)
    session.add(location)
    await session.flush()
    return location


def extract_marker(value: str | None) -> str | None:
    if not value:
        return None
    match = MARKER_RE.search(value)
    return match.group(1) if match else None


async def load_categories(session: AsyncSession) -> dict[str, InventoryCategory]:
    rows = (await session.execute(select(InventoryCategory))).scalars().all()
    return {row.name.lower(): row for row in rows}


async def load_locations(session: AsyncSession) -> dict[str, Location]:
    rows = (await session.execute(select(Location))).scalars().all()
    return {row.name.lower(): row for row in rows}


async def load_inventory_by_marker(session: AsyncSession) -> dict[str, InventoryItem]:
    rows = (await session.execute(select(InventoryItem).where(InventoryItem.description.is_not(None)))).scalars().all()
    return {source_key: row for row in rows if (source_key := extract_marker(row.description))}


async def load_balances(session: AsyncSession) -> dict[tuple[uuid.UUID, uuid.UUID], StockBalance]:
    rows = (await session.execute(select(StockBalance))).scalars().all()
    return {(row.item_id, row.location_id): row for row in rows}


async def import_inventory_items(session: AsyncSession, rows: list[dict[str, Any]]) -> dict[str, int]:
    stats = {"created": 0, "updated": 0}
    categories = await load_categories(session)
    locations = await load_locations(session)
    items_by_marker = await load_inventory_by_marker(session)
    balances = await load_balances(session)

    for row in rows:
        category_name = row["category_name"]
        if category_name.lower() not in categories:
            category = InventoryCategory(id=uuid.uuid4(), name=category_name)
            session.add(category)
            categories[category.name.lower()] = category

        location_name = row["location_name"]
        if location_name.lower() not in locations:
            location = Location(id=uuid.uuid4(), name=location_name)
            session.add(location)
            locations[location.name.lower()] = location

    await session.flush()

    desired_balances: dict[tuple[uuid.UUID, uuid.UUID], int] = {}
    touched_items: list[InventoryItem] = []
    for row in rows:
        category = categories[row["category_name"].lower()]
        location = locations[row["location_name"].lower()]

        item = items_by_marker.get(row["source_key"])
        payload = {
            "item_type": row["item_type"],
            "category_id": category.id,
            "name": row["name"],
            "brand": row.get("brand"),
            "model": row.get("model"),
            "serial_number": row.get("serial_number"),
            "patrimony_number": row.get("patrimony_number"),
            "invoice_number": row.get("invoice_number"),
            "description": row.get("description"),
            "condition_status": row.get("condition_status") or "operacional",
            "current_location_id": location.id,
            "unit": row.get("unit") or "un",
            "minimum_stock_national": int(row.get("minimum_stock_national") or 0),
            "minimum_stock_import": int(row.get("minimum_stock_import") or 0),
            "minimum_stock_maintenance": int(row.get("minimum_stock_maintenance") or 0),
            "ideal_stock": int(row.get("ideal_stock") or 0),
            "is_active": True,
            "deleted_at": None,
        }
        if item:
            for field, value in payload.items():
                setattr(item, field, value)
            item.row_version += 1
            stats["updated"] += 1
        else:
            item = InventoryItem(id=uuid.uuid4(), **payload)
            session.add(item)
            items_by_marker[row["source_key"]] = item
            stats["created"] += 1

        touched_items.append(item)
        desired_balances[(item.id, location.id)] = int(row.get("quantity") or 0)

    await session.flush()

    for balance_key, quantity in desired_balances.items():
        item_id, location_id = balance_key
        balance = balances.get(balance_key)
        if not balance:
            balance = StockBalance(id=uuid.uuid4(), item_id=item_id, location_id=location_id, quantity=0, reserved_quantity=0)
            session.add(balance)
            balances[balance_key] = balance
        balance.quantity = quantity
        balance.reserved_quantity = min(balance.reserved_quantity, balance.quantity)

    for item in touched_items:
        await ensure_stock_alert(session, item)
    return stats


async def find_sensor(session: AsyncSession, row: dict[str, Any]) -> Sensor | None:
    existing = await session.scalar(select(Sensor).where(Sensor.notes.ilike(f"%{marker(row['source_key'])}%")).limit(1))
    if existing:
        return existing
    serial = row.get("serial_number")
    if serial:
        return await session.scalar(
            select(Sensor)
            .where(
                Sensor.deleted_at.is_(None),
                Sensor.serial_number == serial,
                func.lower(Sensor.family) == row["family"].lower(),
            )
            .limit(1)
        )
    return None


async def import_sensors(session: AsyncSession, rows: list[dict[str, Any]]) -> dict[str, int]:
    stats = {"created": 0, "updated": 0}
    existing = (
        await session.execute(select(Sensor).where(Sensor.deleted_at.is_(None), Sensor.notes.is_not(None)))
    ).scalars().all()
    sensors_by_marker = {source_key: row for row in existing if (source_key := extract_marker(row.notes))}
    for row in rows:
        sensor = sensors_by_marker.get(row["source_key"])
        payload = {
            "sensor_type": row["sensor_type"],
            "family": row["family"],
            "brand": row.get("brand"),
            "model": row.get("model"),
            "serial_number": row.get("serial_number"),
            "patrimony_number": row.get("patrimony_number"),
            "operational_status": row.get("operational_status") or "nao_instalado",
            "calibration_due_at": parse_datetime(row.get("calibration_due_at")),
            "notes": row.get("notes"),
            "deleted_at": None,
        }
        if sensor:
            for field, value in payload.items():
                setattr(sensor, field, value)
            stats["updated"] += 1
        else:
            sensor = Sensor(id=uuid.uuid4(), **payload)
            session.add(sensor)
            sensors_by_marker[row["source_key"]] = sensor
            stats["created"] += 1
    return stats


async def import_platforms(session: AsyncSession, rows: list[dict[str, Any]]) -> dict[str, int]:
    stats = {"created": 0, "updated": 0}
    existing = (await session.execute(select(Platform))).scalars().all()
    platforms_by_name = {row.name.lower(): row for row in existing}
    for row in rows:
        platform = platforms_by_name.get(row["name"].lower())
        payload = {
            "name": row["name"],
            "platform_type": row.get("platform_type") or "Estacao",
            "manufacturer": row.get("manufacturer"),
            "model": row.get("model"),
            "operational_status": row.get("operational_status") or "indefinido",
            "description": row.get("description"),
            "deleted_at": None,
        }
        if platform:
            for field, value in payload.items():
                setattr(platform, field, value)
            stats["updated"] += 1
        else:
            platform = Platform(id=uuid.uuid4(), **payload)
            session.add(platform)
            platforms_by_name[platform.name.lower()] = platform
            stats["created"] += 1
    return stats


async def import_checklists(session: AsyncSession, rows: list[dict[str, Any]]) -> dict[str, int]:
    stats = {"created": 0, "updated": 0}
    existing_checklists = (
        await session.execute(select(FieldChecklist).where(FieldChecklist.notes.is_not(None)))
    ).scalars().all()
    checklists_by_marker = {source_key: row for row in existing_checklists if (source_key := extract_marker(row.notes))}
    existing_platforms = (await session.execute(select(Platform).where(Platform.deleted_at.is_(None)))).scalars().all()
    platforms_by_name = {row.name.lower(): row for row in existing_platforms}
    for row in rows:
        checklist = checklists_by_marker.get(row["source_key"])
        platform = platforms_by_name.get(row["platform_name"].lower()) if row.get("platform_name") else None
        submitted_at = parse_datetime(row.get("submitted_at"))
        payload = {
            "title": row["title"],
            "template_name": row["template_name"],
            "platform_id": platform.id if platform else None,
            "platform_name": row.get("platform_name"),
            "status": row.get("status") or "draft",
            "current_step": int(row.get("current_step") or 1),
            "total_steps": int(row.get("total_steps") or 1),
            "answers": row.get("answers") or {},
            "evidence": row.get("evidence") or [],
            "submitted_by_id": int(row.get("submitted_by_id") or 0),
            "submitted_by_username": row.get("submitted_by_username") or "importacao-planilhas",
            "notes": row.get("notes"),
            "submitted_at": submitted_at,
        }
        if checklist:
            for field, value in payload.items():
                setattr(checklist, field, value)
            stats["updated"] += 1
        else:
            checklist = FieldChecklist(id=uuid.uuid4(), **payload)
            session.add(checklist)
            checklists_by_marker[row["source_key"]] = checklist
            stats["created"] += 1
    return stats


async def count_tables(session: AsyncSession) -> dict[str, int]:
    return {
        "inventory_items_active": int(
            await session.scalar(select(func.count()).select_from(InventoryItem).where(InventoryItem.deleted_at.is_(None), InventoryItem.is_active.is_(True)))
            or 0
        ),
        "platforms": int(await session.scalar(select(func.count()).select_from(Platform).where(Platform.deleted_at.is_(None))) or 0),
        "sensors": int(await session.scalar(select(func.count()).select_from(Sensor).where(Sensor.deleted_at.is_(None))) or 0),
        "checklists": int(await session.scalar(select(func.count()).select_from(FieldChecklist)) or 0),
        "checklists_submitted": int(
            await session.scalar(select(func.count()).select_from(FieldChecklist).where(FieldChecklist.status == "submitted")) or 0
        ),
    }


async def run(payload_path: Path, dry_run: bool) -> dict[str, Any]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    async with AsyncSessionLocal() as session:
        print(f"inicio dry_run={dry_run}", flush=True)
        before = await count_tables(session)
        print(f"antes {json.dumps(before, ensure_ascii=False, sort_keys=True)}", flush=True)
        stats = {
            "inventory_items": {},
            "platforms": {},
            "sensors": {},
            "checklists": {},
        }
        stats["inventory_items"] = await import_inventory_items(session, payload.get("inventory_items", []))
        print(f"inventario {json.dumps(stats['inventory_items'], ensure_ascii=False, sort_keys=True)}", flush=True)
        stats["platforms"] = await import_platforms(session, payload.get("platforms", []))
        print(f"plataformas {json.dumps(stats['platforms'], ensure_ascii=False, sort_keys=True)}", flush=True)
        stats["sensors"] = await import_sensors(session, payload.get("sensors", []))
        print(f"sensores {json.dumps(stats['sensors'], ensure_ascii=False, sort_keys=True)}", flush=True)
        stats["checklists"] = await import_checklists(session, payload.get("checklists", []))
        print(f"checklists {json.dumps(stats['checklists'], ensure_ascii=False, sort_keys=True)}", flush=True)
        after = await count_tables(session)
        print(f"depois {json.dumps(after, ensure_ascii=False, sort_keys=True)}", flush=True)
        session.add(
            AuditLog(
                actor_user_id=ACTOR.id,
                actor_username=ACTOR.username,
                actor_roles=ACTOR.roles,
                action="spreadsheet_import_executed",
                entity_type="spreadsheet_import",
                entity_label_snapshot="Carga das planilhas REMOBS",
                after_data={"before": before, "after": after, "stats": stats},
                reason="Carga solicitada pelo usuário a partir das planilhas em docs.",
                source="script",
                status="dry_run" if dry_run else "success",
                audit_metadata={"source_files": payload.get("metadata", {}).get("source_files", [])},
            )
        )
        if dry_run:
            await session.rollback()
        else:
            await session.commit()
        return {"dry_run": dry_run, "before": before, "after": after, "stats": stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa payload de planilhas REMOBS no banco configurado.")
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.payload, args.dry_run)), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
