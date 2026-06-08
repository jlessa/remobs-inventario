from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import subprocess
from typing import Any

import asyncpg


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


async def validate(database_url: str) -> dict[str, object]:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    connection = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://", 1), ssl=context)
    try:
        row = await connection.fetchrow("select current_database() as database_name, current_user as username")
        await connection.execute('create table if not exists "__remobs_permission_probe" (id integer)')
        await connection.execute('drop table "__remobs_permission_probe"')
        return {
            "database": row["database_name"],
            "user_redacted": f"{row['username'][:2]}***",
            "permission_probe": "ok",
        }
    finally:
        await connection.close()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Valida a conexão de banco configurada em um task definition ECS.")
    parser.add_argument("--task-definition", default="remobs-inventario-backend:1")
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

    print(json.dumps(await validate(database_url), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
