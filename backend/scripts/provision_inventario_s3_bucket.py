from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any


DEFAULT_PROFILE = "aws-remobs"
DEFAULT_REGION = "sa-east-1"
DEFAULT_BUCKET = "inventario-remobs"
DEFAULT_PREFIX = "remobs-inventario/"


def run_aws(args: list[str], *, profile: str, region: str, allow_failure: bool = False) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        if allow_failure:
            return {"error": completed.stderr.strip() or completed.stdout.strip()}
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "Falha no AWS CLI.")
    if not completed.stdout.strip():
        return {}
    return json.loads(completed.stdout)


def bucket_exists(*, bucket: str, profile: str, region: str) -> bool:
    result = run_aws(
        ["s3api", "head-bucket", "--bucket", bucket],
        profile=profile,
        region=region,
        allow_failure=True,
    )
    return "error" not in result


def ensure_bucket(*, bucket: str, profile: str, region: str) -> None:
    if bucket_exists(bucket=bucket, profile=profile, region=region):
        print(f"bucket_exists: {bucket}")
        return

    create_args = ["s3api", "create-bucket", "--bucket", bucket]
    if region != "us-east-1":
        create_args.extend(
            [
                "--create-bucket-configuration",
                f"LocationConstraint={region}",
            ]
        )
    run_aws(create_args, profile=profile, region=region)
    print(f"bucket_created: {bucket}")


def harden_bucket(*, bucket: str, profile: str, region: str) -> None:
    run_aws(
        [
            "s3api",
            "put-public-access-block",
            "--bucket",
            bucket,
            "--public-access-block-configuration",
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
        ],
        profile=profile,
        region=region,
    )
    run_aws(
        [
            "s3api",
            "put-bucket-encryption",
            "--bucket",
            bucket,
            "--server-side-encryption-configuration",
            json.dumps(
                {
                    "Rules": [
                        {
                            "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
                            "BucketKeyEnabled": True,
                        }
                    ]
                }
            ),
        ],
        profile=profile,
        region=region,
    )
    run_aws(
        [
            "s3api",
            "put-bucket-versioning",
            "--bucket",
            bucket,
            "--versioning-configuration",
            "Status=Enabled",
        ],
        profile=profile,
        region=region,
    )
    run_aws(
        [
            "s3api",
            "put-bucket-tagging",
            "--bucket",
            bucket,
            "--tagging",
            json.dumps(
                {
                    "TagSet": [
                        {"Key": "Project", "Value": "remobs-inventario"},
                        {"Key": "Environment", "Value": "production"},
                        {"Key": "ManagedBy", "Value": "remobs-inventario-script"},
                    ]
                }
            ),
        ],
        profile=profile,
        region=region,
    )
    deny_insecure = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyInsecureTransport",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"],
                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            }
        ],
    }
    run_aws(
        [
            "s3api",
            "put-bucket-policy",
            "--bucket",
            bucket,
            "--policy",
            json.dumps(deny_insecure),
        ],
        profile=profile,
        region=region,
    )
    print("bucket_hardened: public_block+encryption+versioning+tags+tls_only")


def attach_task_role_policy(
    *,
    task_role_name: str,
    bucket: str,
    prefix: str,
    profile: str,
    region: str,
    policy_name: str,
) -> None:
    normalized_prefix = prefix.strip("/")
    object_arn = f"arn:aws:s3:::{bucket}/{normalized_prefix}/*" if normalized_prefix else f"arn:aws:s3:::{bucket}/*"
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ListBucketPrefix",
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket}"],
                "Condition": {
                    "StringLike": {
                        "s3:prefix": [f"{normalized_prefix}/*" if normalized_prefix else "*"],
                    }
                },
            },
            {
                "Sid": "ObjectReadWriteDelete",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": [object_arn],
            },
        ],
    }
    run_aws(
        [
            "iam",
            "put-role-policy",
            "--role-name",
            task_role_name,
            "--policy-name",
            policy_name,
            "--policy-document",
            json.dumps(policy_doc),
        ],
        profile=profile,
        region=region,
    )
    print(f"task_role_policy_attached: {task_role_name}/{policy_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Provisiona o bucket S3 do inventário REMOBS.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--task-role-name", default="")
    parser.add_argument("--policy-name", default="remobs-inventario-s3-files")
    args = parser.parse_args()

    identity = run_aws(["sts", "get-caller-identity"], profile=args.profile, region=args.region)
    print(json.dumps({"account": identity.get("Account"), "arn": identity.get("Arn")}, sort_keys=True))

    ensure_bucket(bucket=args.bucket, profile=args.profile, region=args.region)
    harden_bucket(bucket=args.bucket, profile=args.profile, region=args.region)

    if args.task_role_name:
        attach_task_role_policy(
            task_role_name=args.task_role_name,
            bucket=args.bucket,
            prefix=args.prefix,
            profile=args.profile,
            region=args.region,
            policy_name=args.policy_name,
        )

    print(
        json.dumps(
            {
                "bucket": args.bucket,
                "region": args.region,
                "prefix": args.prefix.strip("/"),
                "status": "ready",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
