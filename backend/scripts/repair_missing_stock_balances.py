"""Cria saldo ausente no local atual de itens ativos.

Padrão: dry-run. Use --apply --yes para gravar.
Não imprime URL de banco nem credenciais.

Regra: item ativo, com current_location_id, sem nenhuma linha em stock_balances.
Permanente recebe quantidade 1; consumível recebe 0.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Any

import asyncpg


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


async def fetch_items_without_balances(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        """
        select i.id, i.name, i.item_type, i.brand, i.model, i.current_location_id, l.name as location_name
        from inventory_items i
        left join locations l on l.id = i.current_location_id
        where i.deleted_at is null
          and i.is_active = true
          and i.current_location_id is not null
          and not exists (
              select 1 from stock_balances b where b.item_id = i.id
          )
        order by i.name, i.id
        """
    )


def quantity_for(item_type: str) -> int:
    return 1 if item_type == "permanent_component" else 0


async def apply_repair(connection: asyncpg.Connection, rows: list[asyncpg.Record], *, reason: str) -> int:
    if not rows:
        return 0

    now = datetime.now(timezone.utc)
    created = 0
    async with connection.transaction():
        for row in rows:
            quantity = quantity_for(row["item_type"])
            await connection.execute(
                """
                insert into stock_balances (id, item_id, location_id, quantity, reserved_quantity, updated_at)
                values ($1, $2, $3, $4, 0, $5)
                """,
                uuid.uuid4(),
                row["id"],
                row["current_location_id"],
                quantity,
                now,
            )
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
                "repair-missing-balances",
                json.dumps(["system"], ensure_ascii=False),
                "stock_balance_repaired",
                "inventory_item",
                str(row["id"]),
                row["name"],
                json.dumps({"balances": []}, ensure_ascii=False),
                json.dumps(
                    {
                        "location_id": str(row["current_location_id"]),
                        "location_name": row["location_name"],
                        "quantity": quantity,
                    },
                    ensure_ascii=False,
                ),
                json.dumps({"repair": "missing_balance"}, ensure_ascii=False),
                reason,
                "script",
                "success",
                json.dumps({"repair": "missing_balance"}, ensure_ascii=False),
            )
            created += 1
    return created


async def run(args: argparse.Namespace) -> dict[str, Any]:
    database_url = database_url_from_task_definition(
        task_definition=args.task_definition,
        profile=args.profile,
        region=args.region,
    )
    connection = await connect(database_url)
    try:
        rows = await fetch_items_without_balances(connection)
        report: dict[str, Any] = {
            "mode": "apply" if args.apply else "dry-run",
            "task_definition": args.task_definition,
            "profile": args.profile,
            "region": args.region,
            "items_without_balances": len(rows),
            "items": [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "item_type": row["item_type"],
                    "brand": row["brand"],
                    "model": row["model"],
                    "location_name": row["location_name"],
                    "quantity": quantity_for(row["item_type"]),
                }
                for row in rows
            ],
        }
        if args.apply:
            if not args.yes:
                raise SystemExit("Para aplicar, passe --apply --yes.")
            report["created_balances"] = await apply_repair(connection, rows, reason=args.reason)
            remaining = await fetch_items_without_balances(connection)
            report["items_without_balances_after"] = len(remaining)
        return report
    finally:
        await connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria saldo ausente no local atual (dry-run por padrão).")
    parser.add_argument("--task-definition", default="remobs-inventario-backend")
    parser.add_argument("--profile", default="aws-remobs")
    parser.add_argument("--region", default="sa-east-1")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument(
        "--reason",
        default="Reparo: criar saldo no local atual de itens ativos sem stock_balances",
    )
    args = parser.parse_args()
    report = asyncio.run(run(args))
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
