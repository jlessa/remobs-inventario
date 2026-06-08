from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = "default"
DEFAULT_REGION = "sa-east-1"
DEFAULT_TASK_DEFINITION = "remobs-inventario-backend:2"


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def task_environment(task_definition: dict[str, Any]) -> dict[str, str]:
    container = task_definition["taskDefinition"]["containerDefinitions"][0]
    return {item["name"]: item.get("value", "") for item in container.get("environment", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa Alembic usando configuração de banco do task definition.")
    parser.add_argument("--task-definition", default=DEFAULT_TASK_DEFINITION)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
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

    process_env = os.environ.copy()
    process_env["REMOBS_DATABASE_URL"] = database_url
    process_env["REMOBS_DATABASE_SSL"] = environment.get("REMOBS_DATABASE_SSL", "require")
    process_env.pop("REMOBS_DATABASE_SCHEMA", None)

    repo_root = Path(__file__).resolve().parents[2]
    command = [sys.executable, "-m", "alembic", "-c", str(repo_root / "backend" / "alembic.ini"), "upgrade", "head"]
    completed = subprocess.run(command, cwd=repo_root, env=process_env, check=False, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    print(json.dumps({"migration": "ok", "task_definition": args.task_definition}, sort_keys=True))


if __name__ == "__main__":
    main()
