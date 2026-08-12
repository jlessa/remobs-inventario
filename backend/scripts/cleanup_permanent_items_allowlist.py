"""Soft-delete de componentes permanentes fora da allowlist.

Padrão: dry-run (somente relatório). Use --apply para gravar.

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
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import asyncpg


ALLOWED_NAMES = (
    "ACDC",
    "LANTERNA",
    "PAINEL SOLAR",
    "ESTACAO METEOROLOGICA",
    "PLUVIOMETRO",
    "ANEMOMETRO",
)


def normalize_name(value: str | None) -> str:
    text = (value or "").strip().upper()
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


ALLOWED_NORMALIZED = {normalize_name(name) for name in ALLOWED_NAMES}


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


def dsn_from_sqlalchemy_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def connect(database_url: str) -> asyncpg.Connection:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return await asyncpg.connect(dsn_from_sqlalchemy_url(database_url), ssl=context)


async def fetch_active_permanents(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        """
        select id, name, brand, model, serial_number, category_id, is_active, deleted_at, row_version
        from inventory_items
        where item_type = 'permanent_component'
          and deleted_at is null
        order by name, id
        """
    )


def classify(rows: list[asyncpg.Record]) -> tuple[list[asyncpg.Record], list[asyncpg.Record]]:
    keep: list[asyncpg.Record] = []
    delete: list[asyncpg.Record] = []
    for row in rows:
        if normalize_name(row["name"]) in ALLOWED_NORMALIZED:
            keep.append(row)
        else:
            delete.append(row)
    return keep, delete


def summarize(rows: list[asyncpg.Record]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[normalize_name(row["name"]) or "(vazio)"] += 1
    return [{"name_normalized": name, "count": count} for name, count in counter.most_common()]


async def apply_soft_delete(connection: asyncpg.Connection, rows: list[asyncpg.Record], *, reason: str) -> int:
    if not rows:
        return 0

    now = datetime.now(timezone.utc)
    actor_username = "cleanup-permanent-allowlist"
    updated = 0

    async with connection.transaction():
        for row in rows:
            item_id = row["id"]
            result = await connection.execute(
                """
                update inventory_items
                set is_active = false,
                    deleted_at = $2,
                    row_version = row_version + 1,
                    updated_at = $2
                where id = $1
                  and deleted_at is null
                  and item_type = 'permanent_component'
                """,
                item_id,
                now,
            )
            if result.endswith("UPDATE 1"):
                updated += 1
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
                    actor_username,
                    json.dumps(["system"], ensure_ascii=False),
                    "inventory_item_deleted",
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
                            "row_version": row["row_version"],
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "deleted_at": now.isoformat(),
                            "is_active": False,
                            "cleanup": "permanent_allowlist",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps({"cleanup": "permanent_allowlist"}, ensure_ascii=False),
                    reason,
                    "script",
                    "success",
                    json.dumps({"cleanup": "permanent_allowlist"}, ensure_ascii=False),
                )
    return updated


async def run(args: argparse.Namespace) -> dict[str, Any]:
    database_url = database_url_from_task_definition(
        task_definition=args.task_definition,
        profile=args.profile,
        region=args.region,
    )
    connection = await connect(database_url)
    try:
        rows = await fetch_active_permanents(connection)
        keep, delete = classify(rows)

        report: dict[str, Any] = {
            "mode": "apply" if args.apply else "dry-run",
            "task_definition": args.task_definition,
            "profile": args.profile,
            "region": args.region,
            "allowlist_normalized": sorted(ALLOWED_NORMALIZED),
            "total_active_permanents": len(rows),
            "keep_count": len(keep),
            "delete_count": len(delete),
            "keep_by_name": summarize(keep),
            "delete_by_name": summarize(delete),
            "delete_sample": [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "brand": row["brand"],
                    "model": row["model"],
                    "serial_number": row["serial_number"],
                }
                for row in delete[:25]
            ],
            "missing_allowlist_names": sorted(
                name for name in ALLOWED_NORMALIZED if name not in {normalize_name(r["name"]) for r in rows}
            ),
        }

        if args.apply:
            if not args.yes:
                raise SystemExit("Para aplicar, passe --apply --yes após revisar o dry-run.")
            updated = await apply_soft_delete(
                connection,
                delete,
                reason=args.reason,
            )
            remaining = await fetch_active_permanents(connection)
            keep_after, delete_after = classify(remaining)
            report["applied"] = updated
            report["after_total_active_permanents"] = len(remaining)
            report["after_keep_count"] = len(keep_after)
            report["after_delete_candidates"] = len(delete_after)
            report["after_keep_by_name"] = summarize(keep_after)

        return report
    finally:
        await connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Soft-delete de permanent_component fora da allowlist (dry-run por padrão)."
    )
    parser.add_argument("--task-definition", default="remobs-inventario-backend")
    parser.add_argument("--profile", default="aws-remobs")
    parser.add_argument("--region", default="sa-east-1")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Executa soft-delete. Sem esta flag, apenas relata.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma a gravação junto com --apply.",
    )
    parser.add_argument(
        "--reason",
        default="Limpeza produção: manter apenas ACDC, LANTERNA, PAINEL SOLAR, ESTAÇÃO METEOROLÓGICA, PLUVIOMETRO, ANEMOMETRO",
    )
    args = parser.parse_args()
    report = asyncio.run(run(args))
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
