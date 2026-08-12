"""Restaura itens permanentes ADCP soft-deletados.

Padrão: dry-run. Use --apply --yes para gravar.
Não imprime URL de banco nem credenciais.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import ssl
import subprocess
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Any

import asyncpg


TARGET_NAME = "ADCP"


def normalize_name(value: str | None) -> str:
    text = (value or "").strip().upper()
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


def database_url_from_task_definition(*, task_definition: str, profile: str, region: str) -> str:
    payload = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", task_definition],
        profile=profile,
        region=region,
    )
    environment = task_environment(payload)
    database_url = environment.get("REMOBS_DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("REMOBS_DATABASE_URL ausente no task definition.")
    return database_url


async def connect(database_url: str) -> asyncpg.Connection:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    dsn = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return await asyncpg.connect(dsn, ssl=context)


async def fetch_deleted_adcp(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    rows = await connection.fetch(
        """
        select id, name, brand, model, serial_number, is_active, deleted_at, row_version
        from inventory_items
        where item_type = 'permanent_component'
          and deleted_at is not null
        order by deleted_at, name, id
        """
    )
    return [row for row in rows if normalize_name(row["name"]) == TARGET_NAME]


async def apply_restore(connection: asyncpg.Connection, rows: list[asyncpg.Record], *, reason: str) -> int:
    if not rows:
        return 0

    now = datetime.now(timezone.utc)
    restored = 0
    async with connection.transaction():
        for row in rows:
            item_id = row["id"]
            result = await connection.execute(
                """
                update inventory_items
                set is_active = true,
                    deleted_at = null,
                    row_version = row_version + 1,
                    updated_at = $2
                where id = $1
                  and deleted_at is not null
                  and item_type = 'permanent_component'
                """,
                item_id,
                now,
            )
            if not result.endswith("UPDATE 1"):
                continue
            restored += 1
            await connection.execute(
                """
                insert into audit_logs (
                    id, occurred_at, actor_user_id, actor_username, actor_roles,
                    action, entity_type, entity_id, entity_label_snapshot,
                    before_data, after_data, diff, reason, source, status, metadata
                ) values (
                    $1, $2, $3, $4, $5::jsonb,
                    $6, $7, $8, $9,
                    $10::jsonb, $11::jsonb, $12::jsonb, $13, $14, $15, $16::jsonb
                )
                """,
                uuid.uuid4(),
                now,
                0,
                "restore-adcp",
                json.dumps(["system"], ensure_ascii=False),
                "inventory_item_restored",
                "inventory_item",
                str(item_id),
                row["name"],
                json.dumps(
                    {
                        "id": str(item_id),
                        "name": row["name"],
                        "brand": row["brand"],
                        "model": row["model"],
                        "serial_number": row["serial_number"],
                        "is_active": row["is_active"],
                        "deleted_at": row["deleted_at"].isoformat() if row["deleted_at"] else None,
                        "row_version": row["row_version"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "is_active": True,
                        "deleted_at": None,
                        "restore": "adcp",
                    },
                    ensure_ascii=False,
                ),
                json.dumps({"restore": "adcp"}, ensure_ascii=False),
                reason,
                "script",
                "success",
                json.dumps({"restore": "adcp"}, ensure_ascii=False),
            )
    return restored


async def run(args: argparse.Namespace) -> dict[str, Any]:
    database_url = database_url_from_task_definition(
        task_definition=args.task_definition,
        profile=args.profile,
        region=args.region,
    )
    connection = await connect(database_url)
    try:
        rows = await fetch_deleted_adcp(connection)
        report: dict[str, Any] = {
            "mode": "apply" if args.apply else "dry-run",
            "target_name": TARGET_NAME,
            "task_definition": args.task_definition,
            "profile": args.profile,
            "region": args.region,
            "deleted_adcp_count": len(rows),
            "items": [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "brand": row["brand"],
                    "model": row["model"],
                    "serial_number": row["serial_number"],
                    "deleted_at": row["deleted_at"].isoformat() if row["deleted_at"] else None,
                }
                for row in rows
            ],
        }
        if args.apply:
            if not args.yes:
                raise SystemExit("Para aplicar, passe --apply --yes.")
            restored = await apply_restore(connection, rows, reason=args.reason)
            remaining = await fetch_deleted_adcp(connection)
            active = await connection.fetch(
                """
                select id, name, brand, model, serial_number
                from inventory_items
                where item_type = 'permanent_component'
                  and deleted_at is null
                order by name, id
                """
            )
            active_adcp = [row for row in active if normalize_name(row["name"]) == TARGET_NAME]
            report["restored"] = restored
            report["deleted_adcp_remaining"] = len(remaining)
            report["active_adcp_count"] = len(active_adcp)
            report["active_permanents_total"] = len(active)
            report["active_adcp"] = [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "brand": row["brand"],
                    "model": row["model"],
                    "serial_number": row["serial_number"],
                }
                for row in active_adcp
            ]
        return report
    finally:
        await connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaura ADCP soft-deletados (dry-run por padrão).")
    parser.add_argument("--task-definition", default="remobs-inventario-backend")
    parser.add_argument("--profile", default="aws-remobs")
    parser.add_argument("--region", default="sa-east-1")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument(
        "--reason",
        default="Restore ADCP soft-deletados por engano na limpeza de permanentes",
    )
    args = parser.parse_args()
    report = asyncio.run(run(args))
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
