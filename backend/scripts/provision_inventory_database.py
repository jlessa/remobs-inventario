from __future__ import annotations

import asyncio
import json
import os
import ssl as ssl_lib

import asyncpg
from asyncpg import exceptions as asyncpg_exceptions


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    return value


def quote_identifier(value: str) -> str:
    return f'"{value.replace(chr(34), chr(34) + chr(34))}"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def ssl_argument() -> ssl_lib.SSLContext | None:
    value = os.environ.get("REMOBS_DATABASE_SSL", "").strip().lower()
    if value in {"1", "true", "yes", "require", "required"}:
        context = ssl_lib.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl_lib.CERT_NONE
        return context
    return None


async def role_exists(connection: asyncpg.Connection, role_name: str) -> bool:
    return bool(await connection.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", role_name))


async def database_exists(connection: asyncpg.Connection, database_name: str) -> bool:
    return bool(await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", database_name))


async def provision() -> dict[str, object]:
    admin_database_url = required_env("REMOBS_ADMIN_DATABASE_URL")
    admin_inventory_database_url = os.environ.get("REMOBS_ADMIN_INVENTARIO_DATABASE_URL", "").strip()
    app_database_url = required_env("REMOBS_APP_DATABASE_URL")
    database_name = required_env("REMOBS_INVENTARIO_DATABASE_NAME")
    app_user = required_env("REMOBS_INVENTARIO_DATABASE_USER")
    app_password = required_env("REMOBS_INVENTARIO_DATABASE_PASSWORD")

    database_sql = quote_identifier(database_name)
    user_sql = quote_identifier(app_user)
    password_sql = quote_literal(app_password)

    result: dict[str, object] = {
        "database": database_name,
        "user": app_user,
        "role_created": False,
        "role_password_updated": False,
        "database_created": False,
        "database_owner_set_to_app_user": False,
        "permissions_configured": False,
        "schema_owner_set_to_app_user": False,
        "app_connection_validated": False,
    }

    ssl = ssl_argument()

    admin_connection = await asyncpg.connect(admin_database_url, ssl=ssl)
    try:
        if await role_exists(admin_connection, app_user):
            await admin_connection.execute(f"ALTER ROLE {user_sql} WITH LOGIN PASSWORD {password_sql}")
            result["role_password_updated"] = True
        else:
            await admin_connection.execute(f"CREATE ROLE {user_sql} LOGIN PASSWORD {password_sql}")
            result["role_created"] = True

        if await database_exists(admin_connection, database_name):
            try:
                await admin_connection.execute(f"ALTER DATABASE {database_sql} OWNER TO {user_sql}")
                result["database_owner_set_to_app_user"] = True
            except asyncpg_exceptions.InsufficientPrivilegeError:
                result["database_owner_set_to_app_user"] = False
        else:
            try:
                await admin_connection.execute(f"CREATE DATABASE {database_sql} OWNER {user_sql}")
                result["database_owner_set_to_app_user"] = True
            except asyncpg_exceptions.InsufficientPrivilegeError:
                await admin_connection.execute(f"CREATE DATABASE {database_sql}")
            result["database_created"] = True

        await admin_connection.execute(f"REVOKE ALL ON DATABASE {database_sql} FROM PUBLIC")
        await admin_connection.execute(f"GRANT CONNECT ON DATABASE {database_sql} TO {user_sql}")
    finally:
        await admin_connection.close()

    if not admin_inventory_database_url:
        admin_inventory_database_url = admin_database_url.replace("/postgres", f"/{database_name}")

    database_connection = await asyncpg.connect(admin_inventory_database_url, ssl=ssl)
    try:
        await database_connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        await database_connection.execute(f"GRANT USAGE, CREATE ON SCHEMA public TO {user_sql}")
        try:
            await database_connection.execute(f"ALTER SCHEMA public OWNER TO {user_sql}")
            result["schema_owner_set_to_app_user"] = True
        except asyncpg_exceptions.InsufficientPrivilegeError:
            result["schema_owner_set_to_app_user"] = False
        result["permissions_configured"] = True
    finally:
        await database_connection.close()

    app_connection = await asyncpg.connect(app_database_url, ssl=ssl)
    try:
        await app_connection.execute('CREATE TABLE IF NOT EXISTS "__remobs_permission_probe" (id integer)')
        await app_connection.execute('DROP TABLE "__remobs_permission_probe"')
        result["app_connection_validated"] = True
    finally:
        await app_connection.close()

    return result


def main() -> None:
    print(json.dumps(asyncio.run(provision()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
