from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import string
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlsplit

from provision_inventory_database import provision


DEFAULT_REGION = "sa-east-1"
DEFAULT_PROFILE = "default"
SOURCE_TASK_DEFINITION = "api-controle-usuarios-prod-task:3"
DATABASE_NAME = "remobs_inventario"
DATABASE_USER = "remobs_inventario_app"
IMAGE_URI = "220790920077.dkr.ecr.sa-east-1.amazonaws.com/remobs-inventario-backend:prod-2026-06-08-inicial"
TASK_FAMILY = "remobs-inventario-backend"
LOG_GROUP = "/ecs/remobs-inventario-backend"


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


def require_env_value(values: dict[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável ausente no task definition de origem: {name}")
    return value


def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(48))


def database_url(
    *,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    sqlalchemy: bool = False,
    ssl: bool = False,
) -> str:
    driver = "postgresql+asyncpg" if sqlalchemy else "postgresql"
    url = f"{driver}://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{database}"
    return url


def source_database_connection(values: dict[str, str]) -> tuple[str, str, str, str]:
    raw_database_url = values.get("REMOBS_DATABASE_URL", "").strip()
    if raw_database_url:
        normalized_url = raw_database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        parsed = urlsplit(normalized_url)
        if parsed.hostname and parsed.username and parsed.password:
            return (
                parsed.hostname,
                str(parsed.port or 5432),
                unquote(parsed.username),
                unquote(parsed.password),
            )

    return (
        require_env_value(values, "DB_HOST"),
        require_env_value(values, "DB_PORT"),
        require_env_value(values, "DB_USER"),
        require_env_value(values, "DB_PASSWORD"),
    )


def register_task_definition(
    *,
    source_task_definition: dict[str, Any],
    source_environment: dict[str, str],
    app_database_url: str,
    profile: str,
    region: str,
) -> str:
    task_definition = source_task_definition["taskDefinition"]
    execution_role = task_definition["executionRoleArn"]
    task_role = task_definition.get("taskRoleArn")

    payload: dict[str, Any] = {
        "family": TASK_FAMILY,
        "networkMode": "awsvpc",
        "executionRoleArn": execution_role,
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "256",
        "memory": "512",
        "containerDefinitions": [
            {
                "name": TASK_FAMILY,
                "image": IMAGE_URI,
                "essential": True,
                "portMappings": [
                    {
                        "containerPort": 8000,
                        "hostPort": 8000,
                        "protocol": "tcp",
                    }
                ],
                "environment": [
                    {"name": "REMOBS_APP_NAME", "value": "remobs-inventario"},
                    {"name": "REMOBS_ENVIRONMENT", "value": "prod"},
                    {"name": "REMOBS_DEBUG", "value": "false"},
                    {"name": "REMOBS_DATABASE_URL", "value": app_database_url},
                    {"name": "REMOBS_DATABASE_SSL", "value": "require"},
                    {"name": "REMOBS_JWT_SECRET", "value": require_env_value(source_environment, "REMOBS_JWT_SECRET")},
                    {"name": "REMOBS_JWT_ISSUER", "value": require_env_value(source_environment, "REMOBS_JWT_ISSUER")},
                    {"name": "REMOBS_JWT_AUDIENCE", "value": require_env_value(source_environment, "REMOBS_JWT_AUDIENCE")},
                    {"name": "REMOBS_CORS_ORIGINS", "value": "https://inventario.remobs.com.br"},
                ],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": LOG_GROUP,
                        "awslogs-region": region,
                        "awslogs-stream-prefix": TASK_FAMILY,
                    },
                },
            }
        ],
    }

    if task_role:
        payload["taskRoleArn"] = task_role

    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    temp_path = Path(path)
    try:
        temp_path.write_text(json.dumps(payload), encoding="utf-8")
        response = run_aws(
            ["ecs", "register-task-definition", "--cli-input-json", f"file://{temp_path}"],
            profile=profile,
            region=region,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    return response["taskDefinition"]["taskDefinitionArn"]


async def main() -> None:
    parser = argparse.ArgumentParser(description="Provisiona o banco dedicado do REMOBS Inventário a partir do ECS.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--source-task-definition", default=SOURCE_TASK_DEFINITION)
    parser.add_argument("--register-task-definition", action="store_true")
    args = parser.parse_args()

    source_task = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", args.source_task_definition],
        profile=args.profile,
        region=args.region,
    )
    values = task_environment(source_task)

    host, port, admin_user, admin_password = source_database_connection(values)
    app_password = generate_password()

    os.environ["REMOBS_ADMIN_DATABASE_URL"] = database_url(
        user=admin_user,
        password=admin_password,
        host=host,
        port=port,
        database="postgres",
        ssl=True,
    )
    os.environ["REMOBS_APP_DATABASE_URL"] = database_url(
        user=DATABASE_USER,
        password=app_password,
        host=host,
        port=port,
        database=DATABASE_NAME,
        ssl=True,
    )
    os.environ["REMOBS_INVENTARIO_DATABASE_NAME"] = DATABASE_NAME
    os.environ["REMOBS_INVENTARIO_DATABASE_USER"] = DATABASE_USER
    os.environ["REMOBS_INVENTARIO_DATABASE_PASSWORD"] = app_password
    os.environ["REMOBS_DATABASE_SSL"] = "require"

    result = await provision()
    result["task_definition_registered"] = False

    if args.register_task_definition:
        result["task_definition_arn"] = register_task_definition(
            source_task_definition=source_task,
            source_environment=values,
            app_database_url=database_url(
                user=DATABASE_USER,
                password=app_password,
                host=host,
                port=port,
                database=DATABASE_NAME,
                sqlalchemy=True,
            ),
            profile=args.profile,
            region=args.region,
        )
        result["task_definition_registered"] = True

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
