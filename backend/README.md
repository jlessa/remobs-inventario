# REMOBS Inventário Backend

API FastAPI do sistema REMOBS Inventário.

## Execução local

```bash
uvicorn app.main:app --reload --app-dir backend
```

## Container

Build local a partir da raiz do repositório:

```bash
docker build -t remobs-inventario-backend:local -f backend/Dockerfile backend
docker run --rm -p 8000:8000 --env-file backend/.env remobs-inventario-backend:local
```

## Variáveis principais

- `REMOBS_DATABASE_URL`
- `REMOBS_DATABASE_SSL`
- `REMOBS_JWT_SECRET`
- `REMOBS_JWT_ISSUER`
- `REMOBS_JWT_AUDIENCE`
- `REMOBS_CORS_ORIGINS`

Em produção, `REMOBS_DATABASE_URL` deve apontar para o banco PostgreSQL dedicado do inventário no RDS existente. Use `REMOBS_DATABASE_SSL=require` quando o RDS exigir conexão criptografada. Não defina `REMOBS_DATABASE_SCHEMA` em produção.

Migrações no RDS devem ser executadas somente após confirmação explícita.
