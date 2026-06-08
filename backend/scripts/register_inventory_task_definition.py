from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = "default"
DEFAULT_REGION = "sa-east-1"
DEFAULT_SOURCE_TASK_DEFINITION = "remobs-inventario-backend:1"
DEFAULT_IMAGE = "220790920077.dkr.ecr.sa-east-1.amazonaws.com/remobs-inventario-backend:prod-2026-06-08-banco"


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def environment_with_ssl(environment: list[dict[str, str]]) -> list[dict[str, str]]:
    values = {item["name"]: item.get("value", "") for item in environment}
    values["REMOBS_DATABASE_SSL"] = "require"
    return [{"name": key, "value": value} for key, value in values.items()]


def build_payload(task_definition: dict[str, Any], image: str) -> dict[str, Any]:
    source = task_definition["taskDefinition"]
    container = source["containerDefinitions"][0]
    container_payload = {
        "name": container["name"],
        "image": image,
        "essential": container.get("essential", True),
        "portMappings": container.get("portMappings", []),
        "environment": environment_with_ssl(container.get("environment", [])),
        "logConfiguration": container.get("logConfiguration"),
    }

    payload: dict[str, Any] = {
        "family": source["family"],
        "networkMode": source["networkMode"],
        "executionRoleArn": source["executionRoleArn"],
        "requiresCompatibilities": source["requiresCompatibilities"],
        "cpu": source["cpu"],
        "memory": source["memory"],
        "containerDefinitions": [container_payload],
    }
    if source.get("taskRoleArn"):
        payload["taskRoleArn"] = source["taskRoleArn"]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Registra nova revisão do task definition do REMOBS Inventário.")
    parser.add_argument("--source-task-definition", default=DEFAULT_SOURCE_TASK_DEFINITION)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    source = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", args.source_task_definition],
        profile=args.profile,
        region=args.region,
    )
    payload = build_payload(source, args.image)

    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    temp_path = Path(path)
    try:
        temp_path.write_text(json.dumps(payload), encoding="utf-8")
        response = run_aws(
            ["ecs", "register-task-definition", "--cli-input-json", f"file://{temp_path}"],
            profile=args.profile,
            region=args.region,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    print(json.dumps({"task_definition_arn": response["taskDefinition"]["taskDefinitionArn"]}, sort_keys=True))


if __name__ == "__main__":
    main()
