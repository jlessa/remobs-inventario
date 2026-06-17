from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


AUTH_API = os.getenv("SMOKE_AUTH_API", "https://api-controle-usuarios.remobs.com.br")
INVENTORY_API = os.getenv("SMOKE_INVENTORY_API", "https://api-inventario.remobs.com.br")
USERNAME = os.getenv("SMOKE_USERNAME", "")
PASSWORD = os.getenv("SMOKE_PASSWORD", "")


def request(method: str, url: str, *, token: str | None = None, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
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


def count_of(payload: Any) -> Any:
    if isinstance(payload, dict):
        if "total" in payload:
            return payload.get("total")
        if "items" in payload and isinstance(payload["items"], list):
            return len(payload["items"])
        if "items_registered" in payload:
            return payload.get("items_registered")
    if isinstance(payload, list):
        return len(payload)
    return None


def main() -> None:
    if not USERNAME or not PASSWORD:
        raise SystemExit("Defina SMOKE_USERNAME e SMOKE_PASSWORD (sem imprimir o valor).")

    status, login_payload = request("POST", f"{AUTH_API}/auth/login", payload={"username": USERNAME, "password": PASSWORD})
    print(json.dumps({"etapa": "login", "status": status}, ensure_ascii=False))
    if status != 200:
        print(json.dumps({"etapa": "login_erro", "resposta": login_payload}, ensure_ascii=False))
        raise SystemExit(1)
    token = login_payload["access_token"]

    status, me = request("GET", f"{AUTH_API}/users/me", token=token)
    perms = me.get("permission_codes") if isinstance(me, dict) else None
    print(json.dumps({
        "etapa": "users_me",
        "status": status,
        "username": me.get("username") if isinstance(me, dict) else None,
        "is_superuser": me.get("is_superuser") if isinstance(me, dict) else None,
        "qtd_permissoes": len(perms) if isinstance(perms, list) else None,
        "tem_inventory_item_read": ("*" in perms or "inventory:item:read" in perms) if isinstance(perms, list) else None,
    }, ensure_ascii=False))

    endpoints = [
        ("inventory_items", f"{INVENTORY_API}/inventory/items"),
        ("platforms", f"{INVENTORY_API}/platforms"),
        ("sensors", f"{INVENTORY_API}/sensors"),
        ("checklists", f"{INVENTORY_API}/checklists"),
        ("dashboard_summary", f"{INVENTORY_API}/dashboard/summary"),
        ("alerts", f"{INVENTORY_API}/alerts"),
        ("audit_logs", f"{INVENTORY_API}/audit-logs"),
    ]
    for label, url in endpoints:
        status, payload = request("GET", url, token=token)
        record: dict[str, Any] = {"etapa": label, "status": status, "contagem": count_of(payload)}
        if status >= 400:
            record["resposta"] = payload
        print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
