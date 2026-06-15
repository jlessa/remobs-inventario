from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select


TEST_SECRET = "segredo-de-teste-remobs-com-tamanho-seguro"


def _configure_test_environment() -> None:
    db_path = Path(__file__).parent / "test.sqlite"
    if db_path.exists():
        db_path.unlink()

    os.environ["REMOBS_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    os.environ["REMOBS_DATABASE_SCHEMA"] = ""
    os.environ["REMOBS_JWT_SECRET"] = TEST_SECRET
    os.environ["REMOBS_JWT_ISSUER"] = "remobs-users"
    os.environ["REMOBS_JWT_AUDIENCE"] = "remobs-api"
    os.environ["REMOBS_ENVIRONMENT"] = "test"


_configure_test_environment()

from app.core.database import Base, engine  # noqa: E402
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.checklist import FieldChecklist  # noqa: E402
from app.models.inventory import InventoryCategory, InventoryItem, Location, StockBalance, StockMovement  # noqa: E402
from app.models.platform import Hull, Platform, PlatformSystem  # noqa: E402
from app.models.sensor import Sensor, SensorInstallation  # noqa: E402
from app.models.sync import SyncAction  # noqa: E402
from app.models import *  # noqa: F401,F403,E402


def token_for(
    *,
    user_id: int = 7,
    username: str = "operacao",
    permissions: list[str] | None = None,
    roles: list[str] | None = None,
    expires_delta: timedelta = timedelta(hours=1),
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iss": "remobs-users",
        "aud": "remobs-api",
        "iat": now,
        "exp": now + expires_delta,
        "username": username,
        "roles": roles or ["operation"],
        "permissions": permissions or [],
        "resource_access": {},
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.fixture(scope="module", autouse=True)
def database_schema() -> None:
    async def setup() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(setup())


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def auth_headers(permissions: list[str], *, user_id: int = 7, username: str = "operacao") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token_for(user_id=user_id, username=username, permissions=permissions)}",
    }


def run_async(coro):
    return asyncio.run(coro)


def test_inventory_requires_valid_jwt(client: TestClient) -> None:
    response = client.get("/inventory/items")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "not_authenticated",
            "message": "Token de autenticação ausente.",
            "meta": {},
        }
    }


def test_inventory_rejects_missing_permission(client: TestClient) -> None:
    response = client.get("/inventory/items", headers=auth_headers(["platform:read"]))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "permissions_missing"
    assert response.json()["error"]["meta"]["missing_permissions"] == ["inventory:item:read"]


def test_inventory_rejects_expired_jwt(client: TestClient) -> None:
    token = token_for(permissions=["inventory:item:read"], expires_delta=timedelta(seconds=-1))

    response = client.get("/inventory/items", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_expired"


def test_inventory_rejects_wrong_audience(client: TestClient) -> None:
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "7",
            "iss": "remobs-users",
            "aud": "outra-api",
            "iat": now,
            "exp": now + timedelta(hours=1),
            "username": "operacao",
            "roles": ["operation"],
            "permissions": ["inventory:item:read"],
            "resource_access": {},
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    response = client.get("/inventory/items", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token_audience"


def test_inventory_accepts_valid_token_and_lists_items(client: TestClient) -> None:
    response = client.get("/inventory/items", headers=auth_headers(["inventory:item:read"]))

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_creates_inventory_item_with_stock_and_audit_log(client: TestClient) -> None:
    headers = auth_headers(["inventory:item:create", "inventory:item:read", "audit:log:read"])

    response = client.post(
        "/inventory/items",
        headers=headers,
        json={
            "item_type": "consumable",
            "name": "Silicone bisnaga 200 ml",
            "brand": "Dow",
            "model": "200 ml",
            "category_name": "Consumíveis",
            "location_name": "Estoque",
            "unit": "un",
            "initial_quantity": 10,
            "minimum_stock_national": 2,
            "reason": "Carga inicial de teste.",
        },
    )

    assert response.status_code == 201
    item = response.json()
    assert item["name"] == "Silicone bisnaga 200 ml"
    assert item["stock_total"] == 10
    assert item["balances"][0]["quantity"] == 10

    logs_response = client.get("/audit-logs", headers=headers)
    assert logs_response.status_code == 200
    actions = [entry["action"] for entry in logs_response.json()["items"]]
    assert "inventory_item_created" in actions


def test_requests_and_approves_stock_movement(client: TestClient) -> None:
    admin_headers = auth_headers(["*"], user_id=1, username="admin")
    item_response = client.post(
        "/inventory/items",
        headers=admin_headers,
        json={
            "item_type": "consumable",
            "name": f"Cabo teste {uuid.uuid4()}",
            "category_name": "Cabos",
            "location_name": "Estoque",
            "unit": "un",
            "initial_quantity": 5,
            "reason": "Carga inicial.",
        },
    )
    item = item_response.json()
    from_location_id = item["balances"][0]["location_id"]

    request_response = client.post(
        "/inventory/movements/request",
        headers=auth_headers(["inventory:movement:request"], user_id=8, username="campo"),
        json={
            "item_id": item["id"],
            "quantity": 2,
            "from_location_id": from_location_id,
            "to_location_name": "Campo",
            "reason": "Uso em operação de campo.",
        },
    )

    assert request_response.status_code == 201
    movement = request_response.json()
    assert movement["status"] == "pending"

    approve_response = client.post(
        f"/inventory/movements/{movement['id']}/approve",
        headers=admin_headers,
        json={"reason": "Saída autorizada."},
    )

    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    detail_response = client.get(f"/inventory/items/{item['id']}", headers=admin_headers)
    balances = {balance["location_name"]: balance["quantity"] for balance in detail_response.json()["balances"]}
    assert balances["Estoque"] == 3
    assert balances["Campo"] == 2


def test_platform_detail_returns_hull_systems_and_linked_sensors(client: TestClient) -> None:
    async def seed() -> tuple[str, str]:
        async with AsyncSessionLocal() as session:
            platform = Platform(
                name=f"Boia AXYS {uuid.uuid4()}",
                platform_type="boia_fixa",
                manufacturer="AXYS",
                model="3M",
                operational_status="em_operacao",
                description="Plataforma em operação para teste.",
            )
            sensor = Sensor(
                sensor_type="meteorologico",
                family="Anemometro Gill",
                brand="Gill",
                model="WindSonic",
                serial_number=f"SN-{uuid.uuid4()}",
                operational_status="em_operacao",
            )
            session.add_all([platform, sensor])
            await session.flush()
            session.add_all(
                [
                    Hull(platform_id=platform.id, code=f"AX-{uuid.uuid4()}", model="AXYS 3M", status="em_operacao"),
                    PlatformSystem(platform_id=platform.id, name="Energia", status="operacional", notes="Baterias carregadas."),
                    SensorInstallation(sensor_id=sensor.id, platform_id=platform.id, status="ativo", notes="Topo do mastro."),
                ]
            )
            await session.commit()
            return str(platform.id), str(sensor.id)

    platform_id, sensor_id = run_async(seed())

    response = client.get(f"/platforms/{platform_id}", headers=auth_headers(["platform:read"]))

    assert response.status_code == 200
    payload = response.json()
    assert payload["hull"]["status"] == "em_operacao"
    assert payload["systems"][0]["name"] == "Energia"
    assert payload["sensors"][0]["id"] == sensor_id
    assert payload["sensors"][0]["installation_status"] == "ativo"


def test_sensor_detail_returns_current_platform(client: TestClient) -> None:
    async def seed() -> tuple[str, str]:
        async with AsyncSessionLocal() as session:
            platform = Platform(
                name=f"Boia Sensor {uuid.uuid4()}",
                platform_type="boia_fixa",
                operational_status="em_operacao",
            )
            sensor = Sensor(
                sensor_type="oceanografico",
                family="ADCP",
                brand="Nortek",
                model="Aquadopp",
                serial_number=f"ADCP-{uuid.uuid4()}",
                operational_status="em_operacao",
            )
            session.add_all([platform, sensor])
            await session.flush()
            session.add(SensorInstallation(sensor_id=sensor.id, platform_id=platform.id, status="ativo"))
            await session.commit()
            return str(sensor.id), platform.name

    sensor_id, platform_name = run_async(seed())

    response = client.get(f"/sensors/{sensor_id}", headers=auth_headers(["sensor:read"]))

    assert response.status_code == 200
    payload = response.json()
    assert payload["family"] == "ADCP"
    assert payload["current_platform"]["name"] == platform_name
    assert payload["installations"][0]["status"] == "ativo"


def test_checklist_can_be_created_updated_and_submitted(client: TestClient) -> None:
    headers = auth_headers(["checklist:submit"])

    create_response = client.post(
        "/checklists",
        headers=headers,
        json={
            "title": "Checklist AXYS",
            "template_name": "Operacional padrão",
            "platform_name": "Boia AXYS Campo",
            "total_steps": 4,
            "answers": {"energia.baterias_instaladas": True},
        },
    )

    assert create_response.status_code == 201
    checklist = create_response.json()
    assert checklist["status"] == "draft"
    assert checklist["current_step"] == 1

    update_response = client.patch(
        f"/checklists/{checklist['id']}",
        headers=headers,
        json={
            "current_step": 2,
            "answers": {
                "energia.baterias_instaladas": True,
                "energia.quantidade_baterias": 4,
            },
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["answers"]["energia.quantidade_baterias"] == 4

    submit_response = client.post(
        f"/checklists/{checklist['id']}/submit",
        headers=headers,
        json={"reason": "Checklist concluído em campo."},
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "submitted"


def test_sync_conflict_resolution_updates_action_status(client: TestClient) -> None:
    client_action_id = f"offline-{uuid.uuid4()}"

    async def seed() -> None:
        async with AsyncSessionLocal() as session:
            session.add(
                SyncAction(
                    client_action_id=client_action_id,
                    action_type="movement_request",
                    entity_type="stock_movement",
                    payload={"item": "Silicone", "requested_quantity": 4, "server_quantity": 2},
                    user_id=7,
                    username="operacao",
                    status="conflict",
                    error_message="Estoque alterado no servidor.",
                )
            )
            await session.commit()

    run_async(seed())
    headers = auth_headers(["sync:write"], user_id=7, username="operacao")

    conflicts_response = client.get("/sync/conflicts", headers=headers)

    assert conflicts_response.status_code == 200
    assert conflicts_response.json()["items"][0]["client_action_id"] == client_action_id

    resolve_response = client.post(
        "/sync/resolve-conflict",
        headers=headers,
        json={
            "client_action_id": client_action_id,
            "decision": "discard",
            "reason": "Solicitação descartada após conferência de estoque.",
        },
    )

    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "discarded"


def test_dashboard_summary_returns_aggregated_operational_counts(client: TestClient) -> None:
    user_id = 7

    async def seed_and_count() -> dict[str, int]:
        async with AsyncSessionLocal() as session:
            suffix = str(uuid.uuid4())
            category = InventoryCategory(name=f"Categoria dashboard {suffix}")
            location = Location(name=f"Local dashboard {suffix}")
            session.add_all([category, location])
            await session.flush()

            critical_item = InventoryItem(
                item_type="consumable",
                category_id=category.id,
                name=f"Item crítico dashboard {suffix}",
                current_location_id=location.id,
                minimum_stock_national=5,
            )
            healthy_item = InventoryItem(
                item_type="consumable",
                category_id=category.id,
                name=f"Item saudável dashboard {suffix}",
                current_location_id=location.id,
                minimum_stock_national=1,
            )
            platform_operation = Platform(
                name=f"Plataforma em operação {suffix}",
                platform_type="boia_fixa",
                operational_status="em_operacao",
            )
            platform_maintenance = Platform(
                name=f"Plataforma em manutenção {suffix}",
                platform_type="boia_fixa",
                operational_status="em_manutencao",
            )
            broken_sensor = Sensor(
                sensor_type="meteorologico",
                family=f"Sensor com alerta {suffix}",
                operational_status="avariado",
            )
            submitted_checklist = FieldChecklist(
                title=f"Checklist enviado {suffix}",
                template_name="Operacional",
                status="submitted",
                submitted_by_id=user_id,
                submitted_by_username="operacao",
            )
            draft_checklist = FieldChecklist(
                title=f"Checklist rascunho {suffix}",
                template_name="Operacional",
                status="draft",
                submitted_by_id=user_id,
                submitted_by_username="operacao",
            )
            session.add_all(
                [
                    critical_item,
                    healthy_item,
                    platform_operation,
                    platform_maintenance,
                    broken_sensor,
                    submitted_checklist,
                    draft_checklist,
                ]
            )
            await session.flush()
            session.add_all(
                [
                    StockBalance(item_id=critical_item.id, location_id=location.id, quantity=2),
                    StockBalance(item_id=healthy_item.id, location_id=location.id, quantity=3),
                    StockMovement(
                        item_id=critical_item.id,
                        quantity=1,
                        requested_by_id=user_id,
                        requested_by_username="operacao",
                        status="pending",
                        reason="Solicitação pendente de teste.",
                    ),
                    SyncAction(
                        client_action_id=f"pendente-{suffix}",
                        action_type="movement_request",
                        entity_type="stock_movement",
                        payload={},
                        user_id=user_id,
                        username="operacao",
                        status="pending",
                    ),
                    SyncAction(
                        client_action_id=f"conflito-{suffix}",
                        action_type="movement_request",
                        entity_type="stock_movement",
                        payload={},
                        user_id=user_id,
                        username="operacao",
                        status="conflict",
                    ),
                    Alert(
                        alert_type="estoque_minimo",
                        severity="critical",
                        entity_type="inventory_item",
                        entity_id=str(critical_item.id),
                        title=f"Alerta crítico dashboard {suffix}",
                        message="Estoque abaixo do mínimo.",
                        status="open",
                    ),
                ]
            )
            await session.commit()

            stock_totals = (
                select(
                    StockBalance.item_id.label("item_id"),
                    func.coalesce(func.sum(StockBalance.quantity), 0).label("stock_total"),
                )
                .group_by(StockBalance.item_id)
                .subquery()
            )

            return {
                "items_registered": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(InventoryItem)
                        .where(InventoryItem.deleted_at.is_(None), InventoryItem.is_active.is_(True))
                    )
                    or 0
                ),
                "critical_stock": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(InventoryItem)
                        .outerjoin(stock_totals, stock_totals.c.item_id == InventoryItem.id)
                        .where(
                            InventoryItem.deleted_at.is_(None),
                            InventoryItem.is_active.is_(True),
                            InventoryItem.minimum_stock_national > 0,
                            func.coalesce(stock_totals.c.stock_total, 0) < InventoryItem.minimum_stock_national,
                        )
                    )
                    or 0
                ),
                "pending_requests": int(
                    await session.scalar(select(func.count()).select_from(StockMovement).where(StockMovement.status == "pending"))
                    or 0
                ),
                "platforms_in_operation": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(Platform)
                        .where(Platform.deleted_at.is_(None), Platform.operational_status == "em_operacao")
                    )
                    or 0
                ),
                "platforms_in_maintenance": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(Platform)
                        .where(
                            Platform.deleted_at.is_(None),
                            Platform.operational_status.in_(["manutencao", "em_manutencao", "offline"]),
                        )
                    )
                    or 0
                ),
                "sensors_with_alert": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(Sensor)
                        .where(Sensor.deleted_at.is_(None), Sensor.operational_status.in_(["avariado", "inconsistencia"]))
                    )
                    or 0
                ),
                "checklists_registered": int(
                    await session.scalar(select(func.count()).select_from(FieldChecklist)) or 0
                ),
                "checklists_submitted": int(
                    await session.scalar(
                        select(func.count()).select_from(FieldChecklist).where(FieldChecklist.status == "submitted")
                    )
                    or 0
                ),
                "offline_pending": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(SyncAction)
                        .where(SyncAction.user_id == user_id, SyncAction.status == "pending")
                    )
                    or 0
                ),
                "offline_conflicts": int(
                    await session.scalar(
                        select(func.count())
                        .select_from(SyncAction)
                        .where(SyncAction.user_id == user_id, SyncAction.status == "conflict")
                    )
                    or 0
                ),
            }

    expected = run_async(seed_and_count())

    response = client.get("/dashboard/summary", headers=auth_headers(["*"], user_id=user_id))

    assert response.status_code == 200
    payload = response.json()
    for key, value in expected.items():
        assert payload[key] == value
    assert payload["critical_stock_items"][0]["stock_total"] < payload["critical_stock_items"][0]["minimum_stock_national"]
    assert payload["critical_alerts"][0]["severity"] == "critical"
