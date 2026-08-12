from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.pnboia_platforms import (  # noqa: E402
    IMPORT_MARKER_PREFIX,
    SENSOR_MARKER_PREFIX,
    fetch_platform_payloads,
)


def run_aws(args: list[str], *, profile: str, region: str) -> Any:
    command = ["aws", *args, "--profile", profile, "--region", region, "--output", "json"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def load_database_url_from_ecs(*, profile: str, region: str, cluster: str, service: str) -> str:
    services = run_aws(
        ["ecs", "describe-services", "--cluster", cluster, "--services", service],
        profile=profile,
        region=region,
    )
    task_definition = services["services"][0]["taskDefinition"]
    td = run_aws(
        ["ecs", "describe-task-definition", "--task-definition", task_definition],
        profile=profile,
        region=region,
    )
    env = {
        item["name"]: item.get("value", "")
        for item in td["taskDefinition"]["containerDefinitions"][0].get("environment", [])
    }
    db_url = env.get("REMOBS_DATABASE_URL")
    if not db_url:
        raise RuntimeError("REMOBS_DATABASE_URL ausente na task definition.")
    return db_url


def unique_name(desired: str, used: set[str], external_id: int) -> str:
    base = desired[:180]
    if base not in used:
        return base
    suffix = f" #{external_id}"
    candidate = f"{base[: 180 - len(suffix)]}{suffix}"
    if candidate not in used:
        return candidate
    index = 2
    while True:
        suffix = f" #{external_id}-{index}"
        candidate = f"{base[: 180 - len(suffix)]}{suffix}"
        if candidate not in used:
            return candidate
        index += 1


def upsert_hull(cur, *, platform_id: str, hull: dict[str, Any], now: datetime) -> str:
    code = hull["code"]
    cur.execute("SELECT id::text FROM hulls WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        hull_id = row[0]
        cur.execute(
            """
            UPDATE hulls
            SET platform_id = %s::uuid,
                model = %s,
                status = %s,
                notes = %s
            WHERE id = %s::uuid
            """,
            (platform_id, hull.get("model"), hull.get("status"), hull.get("notes"), hull_id),
        )
        return hull_id

    hull_id = str(uuid.uuid4())
    cur.execute(
        """
        INSERT INTO hulls (id, platform_id, code, model, status, notes)
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s)
        """,
        (hull_id, platform_id, code, hull.get("model"), hull.get("status"), hull.get("notes")),
    )
    return hull_id


def upsert_systems(cur, *, platform_id: str, systems: list[dict[str, Any]]) -> int:
    # Remove sistemas anteriores gerados por import PNBOIA deste platform e recria de forma idempotente por nome.
    count = 0
    for system in systems:
        cur.execute(
            """
            SELECT id::text
            FROM platform_systems
            WHERE platform_id = %s::uuid AND name = %s
            """,
            (platform_id, system["name"]),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE platform_systems
                SET status = %s, notes = %s
                WHERE id = %s::uuid
                """,
                (system.get("status"), system.get("notes"), row[0]),
            )
        else:
            cur.execute(
                """
                INSERT INTO platform_systems (id, platform_id, name, status, notes)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s)
                """,
                (str(uuid.uuid4()), platform_id, system["name"], system.get("status"), system.get("notes")),
            )
        count += 1
    return count


def upsert_sensor_with_installation(
    cur,
    *,
    platform_id: str,
    sensor: dict[str, Any],
    now: datetime,
) -> str:
    marker = sensor["marker"]
    serial = sensor.get("serial_number")

    cur.execute(
        """
        SELECT id::text, notes
        FROM sensors
        WHERE deleted_at IS NULL
          AND (
            serial_number = %s
            OR notes LIKE %s
          )
        ORDER BY created_at
        LIMIT 1
        """,
        (serial, f"%{marker}%"),
    )
    row = cur.fetchone()
    if row:
        sensor_id = row[0]
        cur.execute(
            """
            UPDATE sensors
            SET sensor_type = %s,
                family = %s,
                brand = %s,
                model = %s,
                serial_number = %s,
                operational_status = %s,
                notes = %s,
                updated_at = %s,
                deleted_at = NULL
            WHERE id = %s::uuid
            """,
            (
                sensor["sensor_type"],
                sensor["family"],
                sensor.get("brand"),
                sensor.get("model"),
                serial,
                sensor.get("operational_status"),
                sensor.get("notes"),
                now,
                sensor_id,
            ),
        )
    else:
        sensor_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO sensors (
                id, sensor_type, family, brand, model, serial_number,
                operational_status, notes, created_at, updated_at
            )
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                sensor_id,
                sensor["sensor_type"],
                sensor["family"],
                sensor.get("brand"),
                sensor.get("model"),
                serial,
                sensor.get("operational_status"),
                sensor.get("notes"),
                now,
                now,
            ),
        )

    # Installation ativo
    cur.execute(
        """
        SELECT id::text
        FROM sensor_installations
        WHERE sensor_id = %s::uuid AND platform_id = %s::uuid
        ORDER BY installed_at NULLS LAST
        LIMIT 1
        """,
        (sensor_id, platform_id),
    )
    install = cur.fetchone()
    if install:
        cur.execute(
            """
            UPDATE sensor_installations
            SET status = 'ativo',
                removed_at = NULL,
                notes = %s,
                installed_at = COALESCE(installed_at, %s)
            WHERE id = %s::uuid
            """,
            (sensor.get("installation_notes"), now, install[0]),
        )
    else:
        cur.execute(
            """
            INSERT INTO sensor_installations (
                id, sensor_id, platform_id, installed_at, status, notes
            )
            VALUES (%s::uuid, %s::uuid, %s::uuid, %s, 'ativo', %s)
            """,
            (str(uuid.uuid4()), sensor_id, platform_id, now, sensor.get("installation_notes")),
        )
    return sensor_id


def import_platforms(conn, payloads: list[dict[str, Any]]) -> dict[str, Any]:
    cur = conn.cursor()
    now = datetime.now(timezone.utc)

    cur.execute("SELECT id::text, name, description, deleted_at IS NOT NULL FROM platforms")
    existing_rows = cur.fetchall()
    by_marker: dict[str, tuple[str, str, bool]] = {}
    used_names: set[str] = set()
    for platform_id, name, description, deleted in existing_rows:
        used_names.add(name)
        text = description or ""
        for line in text.splitlines():
            if line.startswith(IMPORT_MARKER_PREFIX):
                by_marker[line.strip()] = (platform_id, name, deleted)
                break

    created = 0
    updated = 0
    restored = 0
    hulls = 0
    systems = 0
    sensors = 0
    metadata_errors = 0
    results: list[dict[str, Any]] = []

    for payload in payloads:
        if payload.get("metadata_error"):
            metadata_errors += 1
        marker = f"{IMPORT_MARKER_PREFIX}{payload['external_id']}"
        existing = by_marker.get(marker)
        if existing:
            platform_id, current_name, deleted = existing
            cur.execute(
                """
                UPDATE platforms
                SET platform_type = %s,
                    manufacturer = %s,
                    model = %s,
                    operational_status = %s,
                    description = %s,
                    updated_at = %s,
                    deleted_at = NULL
                WHERE id = %s::uuid
                """,
                (
                    payload["platform_type"],
                    payload["manufacturer"],
                    payload["model"],
                    payload["operational_status"],
                    payload["description"],
                    now,
                    platform_id,
                ),
            )
            updated += 1
            if deleted:
                restored += 1
            name = current_name
            action = "restored" if deleted else "updated"
        else:
            name = unique_name(payload["name"], used_names, payload["external_id"])
            used_names.add(name)
            platform_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO platforms (
                    id, name, platform_type, manufacturer, model, operational_status, description, created_at, updated_at
                )
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id::text
                """,
                (
                    platform_id,
                    name,
                    payload["platform_type"],
                    payload["manufacturer"],
                    payload["model"],
                    payload["operational_status"],
                    payload["description"],
                    now,
                    now,
                ),
            )
            platform_id = cur.fetchone()[0]
            created += 1
            by_marker[marker] = (platform_id, name, False)
            action = "created"

        if payload.get("hull"):
            upsert_hull(cur, platform_id=platform_id, hull=payload["hull"], now=now)
            hulls += 1

        if payload.get("systems"):
            systems += upsert_systems(cur, platform_id=platform_id, systems=payload["systems"])

        sensor_ids = []
        for sensor in payload.get("sensors") or []:
            sensor_ids.append(
                upsert_sensor_with_installation(cur, platform_id=platform_id, sensor=sensor, now=now)
            )
            sensors += 1

        results.append(
            {
                "action": action,
                "id": platform_id,
                "name": name,
                "external_id": payload["external_id"],
                "operational_status": payload["operational_status"],
                "is_active": payload["is_active"],
                "hull": bool(payload.get("hull")),
                "systems": len(payload.get("systems") or []),
                "sensors": len(sensor_ids),
                "metadata_error": payload.get("metadata_error"),
            }
        )

    cur.execute("SELECT COUNT(*) FROM platforms WHERE deleted_at IS NULL")
    active_rows = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*)
        FROM platforms
        WHERE deleted_at IS NULL
          AND operational_status IN ('em_operacao', 'disponivel')
        """
    )
    operative_rows = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hulls WHERE code LIKE 'PNBOIA-HULL-%'")
    hull_rows = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sensors WHERE deleted_at IS NULL AND notes LIKE %s", (f"%{SENSOR_MARKER_PREFIX}%",))
    sensor_rows = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*)
        FROM platform_systems ps
        JOIN platforms p ON p.id = ps.platform_id
        WHERE p.deleted_at IS NULL
          AND p.description LIKE %s
        """,
        (f"%{IMPORT_MARKER_PREFIX}%",),
    )
    system_rows = cur.fetchone()[0]

    conn.commit()
    cur.close()
    return {
        "created": created,
        "updated": updated,
        "restored": restored,
        "hulls_upserted": hulls,
        "systems_upserted": systems,
        "sensors_upserted": sensors,
        "metadata_errors": metadata_errors,
        "total_payloads": len(payloads),
        "platforms_active_rows": active_rows,
        "platforms_operative_status": operative_rows,
        "hull_rows": hull_rows,
        "system_rows": system_rows,
        "sensor_rows": sensor_rows,
        "items": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa boias PNBOIA com metadados, cascos, sistemas e sensores."
    )
    parser.add_argument("--database-url", default=os.getenv("REMOBS_DATABASE_URL"))
    parser.add_argument("--from-ecs", action="store_true")
    parser.add_argument("--profile", default=os.getenv("AWS_PROFILE", "aws-remobs"))
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "sa-east-1"))
    parser.add_argument("--cluster", default="remobs-inventario-cluster")
    parser.add_argument("--service", default="remobs-inventario-backend")
    parser.add_argument("--pnboia-base-url", default=os.getenv("REMOBS_PNBOIA_BASE_URL", "http://dados.pnboia.org"))
    parser.add_argument("--pnboia-token", default=os.getenv("REMOBS_PNBOIA_TOKEN", "JXlFe-ybjfGGJgJRpKfa"))
    parser.add_argument("--skip-metadata", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_url = args.database_url
    if args.from_ecs:
        db_url = load_database_url_from_ecs(
            profile=args.profile,
            region=args.region,
            cluster=args.cluster,
            service=args.service,
        )
    if not db_url:
        raise SystemExit("Informe --database-url ou --from-ecs.")

    payloads = fetch_platform_payloads(
        base_url=args.pnboia_base_url,
        token=args.pnboia_token,
        include_metadata=not args.skip_metadata,
    )
    summary = {
        "source": f"{args.pnboia_base_url.rstrip('/')}/v1/info/available_buoys + /v1/info/metadata",
        "payloads": len(payloads),
        "active": sum(1 for item in payloads if item["is_active"]),
        "inactive": sum(1 for item in payloads if not item["is_active"]),
        "with_hull": sum(1 for item in payloads if item.get("hull")),
        "systems_total": sum(len(item.get("systems") or []) for item in payloads),
        "sensors_total": sum(len(item.get("sensors") or []) for item in payloads),
        "metadata_errors": sum(1 for item in payloads if item.get("metadata_error")),
    }
    if args.dry_run:
        sample = []
        for item in payloads[:2]:
            sample.append(
                {
                    "external_id": item["external_id"],
                    "name": item["name"],
                    "manufacturer": item["manufacturer"],
                    "model": item["model"],
                    "hull": item.get("hull"),
                    "systems": item.get("systems"),
                    "sensors": item.get("sensors"),
                    "metadata_error": item.get("metadata_error"),
                }
            )
        print(json.dumps({"ok": True, "dry_run": True, **summary, "sample": sample}, ensure_ascii=False, indent=2))
        return 0

    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=(parsed.path or "/").lstrip("/") or "postgres",
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        sslmode="require",
        connect_timeout=20,
    )
    try:
        result = import_platforms(conn, payloads)
    finally:
        conn.close()

    print(
        json.dumps(
            {
                "ok": True,
                "dry_run": False,
                "db_host": parsed.hostname,
                "db_name": (parsed.path or "").lstrip("/"),
                **summary,
                **{k: v for k, v in result.items() if k != "items"},
                "items_preview": result["items"][:8],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
