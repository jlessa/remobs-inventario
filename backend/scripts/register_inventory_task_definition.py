from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = "aws-remobs"
DEFAULT_REGION = "sa-east-1"
DEFAULT_SOURCE_TASK_DEFINITION = "remobs-inventario-backend"
DEFAULT_IMAGE = "220790920077.dkr.ecr.sa-east-1.amazonaws.com/remobs-inventario-backend:latest"
DEFAULT_TASK_ROLE_ARN = "arn:aws:iam::220790920077:role/remobs-inventario-backend-task-role"
DEFAULT_S3_BUCKET = "inventario-remobs"
DEFAULT_S3_PREFIX = "remobs-inventario"


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def environment_with_storage(
    environment: list[dict[str, str]],
    *,
    s3_bucket: str,
    s3_region: str,
    s3_prefix: str,
    enable_s3: bool,
) -> list[dict[str, str]]:
    values = {item["name"]: item.get("value", "") for item in environment}
    values["REMOBS_DATABASE_SSL"] = "require"
    if enable_s3:
        values["REMOBS_STORAGE_BACKEND"] = "s3"
        values["REMOBS_STORAGE_S3_BUCKET"] = s3_bucket
        values["REMOBS_STORAGE_S3_REGION"] = s3_region
        values["REMOBS_STORAGE_S3_PREFIX"] = s3_prefix
    return [{"name": key, "value": value} for key, value in values.items()]


def build_payload(
    task_definition: dict[str, Any],
    image: str,
    *,
    task_role_arn: str | None,
    s3_bucket: str,
    s3_region: str,
    s3_prefix: str,
    enable_s3: bool,
) -> dict[str, Any]:
    source = task_definition["taskDefinition"]
    container = source["containerDefinitions"][0]
    container_payload = {
        "name": container["name"],
        "image": image,
        "essential": container.get("essential", True),
        "portMappings": container.get("portMappings", []),
        "environment": environment_with_storage(
            container.get("environment", []),
            s3_bucket=s3_bucket,
            s3_region=s3_region,
            s3_prefix=s3_prefix,
            enable_s3=enable_s3,
        ),
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
    resolved_task_role = task_role_arn or source.get("taskRoleArn")
    if resolved_task_role:
        payload["taskRoleArn"] = resolved_task_role
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Registra nova revisão do task definition do REMOBS Inventário.")
    parser.add_argument("--source-task-definition", default=DEFAULT_SOURCE_TASK_DEFINITION)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--task-role-arn", default=DEFAULT_TASK_ROLE_ARN)
    parser.add_argument("--s3-bucket", default=DEFAULT_S3_BUCKET)
    parser.add_argument("--s3-prefix", default=DEFAULT_S3_PREFIX)
    parser.add_argument("--enable-s3", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    source = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", args.source_task_definition],
        profile=args.profile,
        region=args.region,
    )
    payload = build_payload(
        source,
        args.image,
        task_role_arn=args.task_role_arn or None,
        s3_bucket=args.s3_bucket,
        s3_region=args.region,
        s3_prefix=args.s3_prefix,
        enable_s3=args.enable_s3,
    )

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
