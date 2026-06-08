from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = "default"
DEFAULT_REGION = "sa-east-1"
DEFAULT_APP_ID = "d1oidnxd2f4saq"
DEFAULT_BRANCH = "prod"


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def zip_directory(source_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir).as_posix())


def upload_zip(zip_path: Path, upload_url: str) -> None:
    data = zip_path.read_bytes()
    request = urllib.request.Request(upload_url, data=data, method="PUT")
    request.add_header("Content-Type", mimetypes.guess_type(zip_path.name)[0] or "application/zip")
    request.add_header("Content-Length", str(len(data)))
    with urllib.request.urlopen(request, timeout=180) as response:
        if response.status >= 400:
            raise RuntimeError(f"Upload do Amplify falhou com status {response.status}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Faz deploy manual do frontend no Amplify.")
    parser.add_argument("--app-id", default=DEFAULT_APP_ID)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--dist", default="frontend/dist")
    args = parser.parse_args()

    dist = Path(args.dist).resolve()
    if not (dist / "index.html").exists():
        raise RuntimeError(f"Artefato inválido: {dist / 'index.html'} não existe.")

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "artifacts.zip"
        zip_directory(dist, zip_path)
        deployment = run_aws(
            ["amplify", "create-deployment", "--app-id", args.app_id, "--branch-name", args.branch],
            profile=args.profile,
            region=args.region,
        )
        upload_zip(zip_path, deployment["zipUploadUrl"])
        job = run_aws(
            [
                "amplify",
                "start-deployment",
                "--app-id",
                args.app_id,
                "--branch-name",
                args.branch,
                "--job-id",
                deployment["jobId"],
            ],
            profile=args.profile,
            region=args.region,
        )

    print(
        json.dumps(
            {
                "app_id": args.app_id,
                "branch": args.branch,
                "job_id": job["jobSummary"]["jobId"],
                "status": job["jobSummary"]["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
