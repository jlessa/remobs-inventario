from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import subprocess
from typing import Any

import asyncpg


EXPECTED_TABLES = [
    "alembic_version",
    "inventory_categories",
    "locations",
    "inventory_items",
    "stock_balances",
    "stock_movements",
    "audit_logs",
    "alerts",
    "files",
    "entity_files",
    "platforms",
    "hulls",
    "platform_systems",
    "system_components",
    "sensors",
    "sensor_installations",
    "sync_actions",
]


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


async def inspect_database(database_url: str) -> dict[str, object]:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    connection = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://", 1), ssl=context)
    try:
        table_rows = await connection.fetch(
            """
            select tablename
            from pg_catalog.pg_tables
            where schemaname = 'public'
            order by tablename
            """
        )
        tables = [row["tablename"] for row in table_rows]
        version = await connection.fetchval("select version_num from alembic_version")
        missing = [table for table in EXPECTED_TABLES if table not in tables]
        return {
            "alembic_version": version,
            "expected_tables_present": not missing,
            "missing_tables": missing,
            "table_count": len(tables),
        }
    finally:
        await connection.close()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Inspeciona tabelas do banco do task definition ECS.")
    parser.add_argument("--task-definition", default="remobs-inventario-backend:2")
    parser.add_argument("--profile", default="default")
    parser.add_argument("--region", default="sa-east-1")
    args = parser.parse_args()

    task_definition = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", args.task_definition],
        profile=args.profile,
        region=args.region,
    )
    environment = task_environment(task_definition)
    database_url = environment.get("REMOBS_DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("REMOBS_DATABASE_URL ausente no task definition.")

    print(json.dumps(await inspect_database(database_url), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
