from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


AUTH_API = os.getenv("SMOKE_AUTH_API", "https://api-controle-usuarios.remobs.com.br")
INVENTORY_API = os.getenv("SMOKE_INVENTORY_API", "https://api-inventario.remobs.com.br")
USERNAME = os.getenv("SMOKE_USERNAME", "")
PASSWORD = os.getenv("SMOKE_PASSWORD", "")


def request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed: Any = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed


def assert_status(label: str, status: int, expected: set[int], payload: Any) -> None:
    if status not in expected:
        print(json.dumps({"etapa": label, "status": status, "resposta": payload}, ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps({"etapa": label, "status": status}, ensure_ascii=False))


def main() -> None:
    if not USERNAME or not PASSWORD:
        raise SystemExit("Defina SMOKE_USERNAME e SMOKE_PASSWORD.")

    status, login_payload = request(
        "POST",
        f"{AUTH_API}/auth/login",
        payload={"username": USERNAME, "password": PASSWORD},
    )
    assert_status("login", status, {200}, {"access_token": "***"} if status == 200 else login_payload)
    token = login_payload["access_token"]

    status, me_payload = request("GET", f"{AUTH_API}/users/me", token=token)
    assert_status("users_me", status, {200}, me_payload)

    status, list_payload = request("GET", f"{INVENTORY_API}/inventory/items", token=token)
    assert_status("inventory_list", status, {200}, list_payload)

    marker = int(time.time())
    status, created = request(
        "POST",
        f"{INVENTORY_API}/inventory/items",
        token=token,
        payload={
            "item_type": "consumable",
            "name": f"Teste Codex Produção {marker}",
            "category_name": "Teste operacional",
            "location_name": "Local de teste operacional",
            "unit": "un",
            "initial_quantity": 2,
            "minimum_stock_national": 1,
            "ideal_stock": 2,
            "reason": "Smoke test de produção autorizado.",
        },
    )
    assert_status("inventory_create", status, {201}, created)
    item_id = created["id"]

    status, item_payload = request("GET", f"{INVENTORY_API}/inventory/items/{item_id}", token=token)
    assert_status("inventory_get", status, {200}, item_payload)

    status, history_payload = request("GET", f"{INVENTORY_API}/inventory/items/{item_id}/history", token=token)
    assert_status("inventory_history", status, {200}, history_payload)

    from_location_id = created["balances"][0]["location_id"]
    status, movement_payload = request(
        "POST",
        f"{INVENTORY_API}/inventory/movements/request",
        token=token,
        payload={
            "item_id": item_id,
            "quantity": 1,
            "from_location_id": from_location_id,
            "to_location_name": "Local de rejeição do smoke test",
            "reason": "Smoke test de solicitação de saída.",
        },
    )
    assert_status("movement_request", status, {201}, movement_payload)
    movement_id = movement_payload["id"]

    status, movement_reject_payload = request(
        "POST",
        f"{INVENTORY_API}/inventory/movements/{movement_id}/reject",
        token=token,
        payload={"reason": "Rejeição controlada do smoke test de produção."},
    )
    assert_status("movement_reject", status, {200}, movement_reject_payload)

    status, movements_payload = request("GET", f"{INVENTORY_API}/inventory/movements", token=token)
    assert_status("movements_list", status, {200}, movements_payload)

    status, alerts_payload = request("GET", f"{INVENTORY_API}/alerts", token=token)
    assert_status("alerts_list", status, {200}, alerts_payload)

    status, platforms_payload = request("GET", f"{INVENTORY_API}/platforms", token=token)
    assert_status("platforms_list", status, {200}, platforms_payload)

    status, sensors_payload = request("GET", f"{INVENTORY_API}/sensors", token=token)
    assert_status("sensors_list", status, {200}, sensors_payload)

    status, sync_payload = request("GET", f"{INVENTORY_API}/sync/status", token=token)
    assert_status("sync_status", status, {200}, sync_payload)

    status, audit_payload = request("GET", f"{INVENTORY_API}/audit-logs", token=token)
    assert_status("audit_logs", status, {200}, audit_payload)

    status, delete_payload = request(
        "DELETE",
        f"{INVENTORY_API}/inventory/items/{item_id}",
        token=token,
        payload={"reason": "Limpeza do item criado pelo smoke test de produção."},
    )
    assert_status("inventory_delete", status, {200}, delete_payload)

    print(json.dumps({"resultado": "ok", "item_teste_removido": item_id}, ensure_ascii=False))


if __name__ == "__main__":
    main()
