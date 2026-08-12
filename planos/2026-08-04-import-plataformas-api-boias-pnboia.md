# Importar plataformas da API de boias PNBOIA e filtro de ativas

## Contexto
As plataformas do inventário foram limpas em produção. O usuário pediu importar todas as boias da API PNBOIA (ativas e inativas), com filtro “Somente ativas” padrão na listagem.

## Objetivo
- Buscar boias em `http://dados.pnboia.org/v1/info/available_buoys`
- Cadastrar metadados disponíveis como plataformas
- Filtrar listagem por ativas (default true)

## Fonte de dados
- Ativas: `operative=true` → 8 boias (`mode=FUNDEADA`)
- Completo: `operative=false` → 45 boias (todas)
- Marcação `is_active` = presença no conjunto operativo

## Metadados gravados
Nome, tipo (`type`), fabricante/modelo, status operacional, descrição com:
`buoy_id`, `local`, lat/lon, `mode`, `metarea_section`, `project_id`, `api_endpoint`, `last_date_time`, marcador `remobs-import:pnboia-buoy:{id}`.

## Resultado em produção
- 45 plataformas criadas (8 ativas / 37 inativas)
- API: `GET /platforms?active_only=true|false` (default true)
- UI: switch “Somente ativas” (default ligado)
- Backend ECS: `remobs-inventario-backend:7`
- Frontend Amplify job `26` SUCCEED
- Script reexecutável: `backend/scripts/import_pnboia_platforms.py --from-ecs`
