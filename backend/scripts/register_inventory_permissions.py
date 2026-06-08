from __future__ import annotations

import argparse
import os
from typing import Iterable

import httpx


PERMISSIONS: list[tuple[str, str]] = [
    ("inventory:item:read", "Consultar itens do inventário"),
    ("inventory:item:create", "Cadastrar itens do inventário"),
    ("inventory:item:update", "Editar itens do inventário"),
    ("inventory:item:delete", "Inativar itens do inventário"),
    ("inventory:movement:request", "Solicitar saída de material"),
    ("inventory:movement:approve", "Aprovar ou reprovar saída de material"),
    ("platform:read", "Consultar plataformas"),
    ("platform:update", "Cadastrar e editar plataformas"),
    ("sensor:read", "Consultar sensores"),
    ("sensor:update", "Cadastrar e editar sensores"),
    ("checklist:submit", "Enviar checklists de campo"),
    ("audit:log:read", "Consultar logs de auditoria"),
    ("sync:write", "Sincronizar ações offline"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Registra permissões do inventário no remobs-users.")
    parser.add_argument("--auth-api", default=os.getenv("REMOBS_AUTH_API_BASE_URL", "http://localhost:8015"))
    parser.add_argument("--token", default=os.getenv("REMOBS_ADMIN_TOKEN"))
    return parser.parse_args()


async def register_permissions(auth_api: str, token: str, permissions: Iterable[tuple[str, str]]) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=auth_api, headers=headers, timeout=10) as client:
        for code, description in permissions:
            response = await client.post("/permissions", json={"code": code, "description": description})
            if response.status_code not in {200, 201, 409}:
                raise RuntimeError(f"Falha ao registrar {code}: {response.status_code} {response.text}")
            print(f"{code}: ok")


def main() -> None:
    args = parse_args()
    if not args.token:
        raise SystemExit("Informe REMOBS_ADMIN_TOKEN ou --token.")

    import asyncio

    asyncio.run(register_permissions(args.auth_api, args.token, PERMISSIONS))


if __name__ == "__main__":
    main()
