from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import secrets
import ssl as ssl_lib
import string
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlsplit

import asyncpg

from provision_inventory_database import provision


DEFAULT_ACCESS_FILE = r"C:\Users\jeffe\AppData\Local\Programs\Syncthing\Pessoal\acesso.txt"
DEFAULT_REGION = "sa-east-1"
DEFAULT_PROFILE = "default"
SOURCE_TASK_DEFINITION = "api-controle-usuarios-prod-task:3"
DATABASE_NAME = "remobs_inventario"
DATABASE_USER = "remobs_inventario_app"
IMAGE_URI = "220790920077.dkr.ecr.sa-east-1.amazonaws.com/remobs-inventario-backend:prod-2026-06-08-inicial"
TASK_FAMILY = "remobs-inventario-backend"
LOG_GROUP = "/ecs/remobs-inventario-backend"


@dataclass(frozen=True)
class DbCandidate:
    label: str
    host: str
    port: str
    user: str
    password: str
    database: str = "postgres"


def ssl_context() -> ssl_lib.SSLContext:
    context = ssl_lib.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl_lib.CERT_NONE
    return context


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


def require_value(values: dict[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Valor obrigatório ausente: {name}")
    return value


def database_url(*, user: str, password: str, host: str, port: str, database: str, sqlalchemy: bool = False) -> str:
    driver = "postgresql+asyncpg" if sqlalchemy else "postgresql"
    return f"{driver}://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{database}"


def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(48))


def key_values(content: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        match = re.match(r"^([A-Za-zÀ-ÿ0-9_. -]{2,80})\s*[:=]\s*(.+?)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip().lower()
        value = match.group(2).strip().strip("\"'")
        values.setdefault(key, []).append(value)
    return values


def first_value(values: dict[str, list[str]], *keys: str) -> str | None:
    for key in keys:
        entries = values.get(key.lower())
        if entries:
            return entries[-1]
    return None


def parse_url_candidates(content: str) -> list[DbCandidate]:
    candidates: list[DbCandidate] = []
    pattern = re.compile(r"postgres(?:ql)?(?:\+asyncpg)?://[^\s\)\]\}\"']+", re.IGNORECASE)
    for index, raw_url in enumerate(pattern.findall(content), start=1):
        normalized = raw_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        parsed = urlsplit(normalized)
        if not (parsed.hostname and parsed.username and parsed.password):
            continue
        candidates.append(
            DbCandidate(
                label=f"url_{index}",
                host=parsed.hostname,
                port=str(parsed.port or 5432),
                user=unquote(parsed.username),
                password=unquote(parsed.password),
                database=parsed.path.lstrip("/") or "postgres",
            )
        )
    return candidates


def parse_field_candidates(content: str) -> list[DbCandidate]:
    values = key_values(content)
    host = first_value(values, "endpoint", "host", "db_host", "db host")
    port = first_value(values, "porta", "port", "db_port") or "5432"
    password = first_value(values, "senha", "password", "db_password", "postgres_password")
    users = [
        value
        for value in [
            first_value(values, "username"),
            first_value(values, "user", "usuario", "usuário"),
            first_value(values, "postgres_user", "db_user"),
            "postgres",
        ]
        if value
    ]
    database = first_value(values, "banco inicial", "postgres_db", "db_name", "database") or "postgres"

    if not (host and password):
        return []

    candidates: list[DbCandidate] = []
    seen: set[tuple[str, str, str]] = set()
    for index, user in enumerate(users, start=1):
        key = (host, port, user)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            DbCandidate(
                label=f"fields_{index}",
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
            )
        )
    return candidates


async def candidate_has_admin_privileges(candidate: DbCandidate) -> bool:
    connection = await asyncpg.connect(
        database_url(
            user=candidate.user,
            password=candidate.password,
            host=candidate.host,
            port=candidate.port,
            database=candidate.database,
        ),
        ssl=ssl_context(),
    )
    try:
        row = await connection.fetchrow(
            "SELECT rolsuper, rolcreaterole, rolcreatedb FROM pg_roles WHERE rolname = current_user"
        )
        if not row:
            return False
        return bool(row["rolsuper"] or (row["rolcreaterole"] and row["rolcreatedb"]))
    finally:
        await connection.close()


async def choose_candidate(candidates: list[DbCandidate]) -> tuple[DbCandidate, list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    for candidate in candidates:
        metadata = {
            "label": candidate.label,
            "host": candidate.host,
            "port": candidate.port,
            "database": candidate.database,
            "user_redacted": f"{candidate.user[:2]}***" if candidate.user else "",
            "connected_with_admin_privileges": False,
        }
        try:
            if await candidate_has_admin_privileges(candidate):
                metadata["connected_with_admin_privileges"] = True
                attempts.append(metadata)
                return candidate, attempts
        except Exception as exc:  # noqa: BLE001
            metadata["error"] = exc.__class__.__name__
        attempts.append(metadata)

    raise RuntimeError(f"Nenhum candidato possui privilégio administrativo suficiente: {attempts}")


def register_task_definition(
    *,
    source_task_definition: dict[str, Any],
    source_environment: dict[str, str],
    app_database_url: str,
    profile: str,
    region: str,
) -> str:
    task_definition = source_task_definition["taskDefinition"]
    payload: dict[str, Any] = {
        "family": TASK_FAMILY,
        "networkMode": "awsvpc",
        "executionRoleArn": task_definition["executionRoleArn"],
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "256",
        "memory": "512",
        "containerDefinitions": [
            {
                "name": TASK_FAMILY,
                "image": IMAGE_URI,
                "essential": True,
                "portMappings": [{"containerPort": 8000, "hostPort": 8000, "protocol": "tcp"}],
                "environment": [
                    {"name": "REMOBS_APP_NAME", "value": "remobs-inventario"},
                    {"name": "REMOBS_ENVIRONMENT", "value": "prod"},
                    {"name": "REMOBS_DEBUG", "value": "false"},
                    {"name": "REMOBS_DATABASE_URL", "value": app_database_url},
                    {"name": "REMOBS_DATABASE_SSL", "value": "require"},
                    {"name": "REMOBS_JWT_SECRET", "value": require_value(source_environment, "REMOBS_JWT_SECRET")},
                    {"name": "REMOBS_JWT_ISSUER", "value": require_value(source_environment, "REMOBS_JWT_ISSUER")},
                    {"name": "REMOBS_JWT_AUDIENCE", "value": require_value(source_environment, "REMOBS_JWT_AUDIENCE")},
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

    if task_definition.get("taskRoleArn"):
        payload["taskRoleArn"] = task_definition["taskRoleArn"]

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
        return response["taskDefinition"]["taskDefinitionArn"]
    finally:
        temp_path.unlink(missing_ok=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Provisiona o banco dedicado do REMOBS Inventário.")
    parser.add_argument("--access-file", default=DEFAULT_ACCESS_FILE)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--register-task-definition", action="store_true")
    args = parser.parse_args()

    content = Path(args.access_file).read_text(encoding="utf-8", errors="ignore")
    candidates = parse_url_candidates(content) + parse_field_candidates(content)
    if not candidates:
        raise RuntimeError("Nenhum candidato de PostgreSQL encontrado no arquivo de acesso.")

    candidate, attempts = await choose_candidate(candidates)
    app_password = generate_password()

    os.environ["REMOBS_ADMIN_DATABASE_URL"] = database_url(
        user=candidate.user,
        password=candidate.password,
        host=candidate.host,
        port=candidate.port,
        database="postgres",
    )
    os.environ["REMOBS_ADMIN_INVENTARIO_DATABASE_URL"] = database_url(
        user=candidate.user,
        password=candidate.password,
        host=candidate.host,
        port=candidate.port,
        database=DATABASE_NAME,
    )
    os.environ["REMOBS_APP_DATABASE_URL"] = database_url(
        user=DATABASE_USER,
        password=app_password,
        host=candidate.host,
        port=candidate.port,
        database=DATABASE_NAME,
    )
    os.environ["REMOBS_INVENTARIO_DATABASE_NAME"] = DATABASE_NAME
    os.environ["REMOBS_INVENTARIO_DATABASE_USER"] = DATABASE_USER
    os.environ["REMOBS_INVENTARIO_DATABASE_PASSWORD"] = app_password
    os.environ["REMOBS_DATABASE_SSL"] = "require"

    result = await provision()
    result["candidate_attempts"] = attempts
    result["selected_candidate"] = {
        "label": candidate.label,
        "host": candidate.host,
        "port": candidate.port,
        "database": candidate.database,
        "user_redacted": f"{candidate.user[:2]}***",
    }
    result["task_definition_registered"] = False

    if args.register_task_definition:
        source_task = run_aws(
            ["ecs", "describe-task-definition", "--task-definition", SOURCE_TASK_DEFINITION],
            profile=args.profile,
            region=args.region,
        )
        result["task_definition_arn"] = register_task_definition(
            source_task_definition=source_task,
            source_environment=task_environment(source_task),
            app_database_url=database_url(
                user=DATABASE_USER,
                password=app_password,
                host=candidate.host,
                port=candidate.port,
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
