# Plano: Autocomplete rápido no cadastro de itens

## Contexto

No cadastro de itens (`InventoryFormPage`), os campos **Nome**, **Marca** e **Modelo** repetem valores já existentes no inventário. Digitar tudo de novo gera inconsistência de grafia e atrasa o cadastro.

## Objetivo

Sugerir valores já usados assim que o usuário digitar **1 letra**, com resposta rápida e sem travar a digitação livre de valores novos.

## Decisão de arquitetura

### Abordagem escolhida: consulta `DISTINCT` nos itens existentes

| Opção | Prós | Contras | Decisão |
| :--- | :--- | :--- | :--- |
| Tabelas dicionário (marcas/modelos) | Normalização forte | Migração, sync, CRUD extra | Descartada por enquanto |
| Carregar lista completa no front | Zero latência após 1ª carga | Payload pesado, desatualiza | Descartada |
| **`GET .../suggestions` com DISTINCT + prefixo + LIMIT** | Simples, sempre atual, leve | Depende de volume do inventário | **Escolhida** |

Motivos:

1. Valores nascem no próprio cadastro — não há dicionário separado para manter.
2. Prefixo (`ILIKE 'a%'`) é amigável a índice e responde bem com 1 caractere.
3. `DISTINCT` + `LIMIT 20` + apenas itens ativos mantém payload mínimo.
4. Índices em `brand` e `model` ( `name` já indexado) aceleram o filtro.
5. Front usa `Autocomplete freeSolo` (aceita valor novo) + debounce curto + cancelamento de request em voo.

### Contrato da API

```
GET /inventory/items/suggestions?field=name|brand|model&q=<texto>&limit=20
Authorization: Bearer <token com inventory:item:read|create>
```

Resposta:

```json
{ "field": "name", "q": "si", "items": ["Silicone bisnaga 200 ml", "..."] }
```

Regras:

- `q` mínimo: 1 caractere (após trim)
- `q` vazio → lista vazia (sem varrer a tabela)
- Match por prefixo, case-insensitive
- Só itens `is_active` e sem `deleted_at`
- Ignora nulos e strings vazias
- `limit` padrão 20, máximo 50

### Frontend

- Componente reutilizável ou lógica no form: MUI `Autocomplete` + `freeSolo`
- Debounce ~150 ms
- Disparo a partir de 1 caractere
- `AbortController` / flag de request para evitar race ao digitar rápido
- Campos: `name`, `brand`, `model`

## Escopo

### Inclui

- Endpoint backend de sugestões
- Função no service de inventário
- Schema de resposta
- Índices `brand` / `model` (migração Alembic)
- Autocomplete no `InventoryFormPage` (nome, marca, modelo, categoria, local)
- Método no `inventoryService` frontend
- Testes de contrato backend e cliente frontend
- `CHANGELOG.md`
- Deploy em produção (ECS + Amplify)

### Fora de escopo

- Preenchimento cruzado (escolher nome e auto-preencher marca/modelo)
- Tabelas de dicionário normalizadas
- Cache em Redis / CDN

## Etapas

1. Backend: schema + service `suggest_item_field_values` + rota `/suggestions`
2. Migração: índices em `inventory_items.brand` e `inventory_items.model`
3. Frontend: service + form com Autocomplete
4. Testes e changelog
5. Validar com suite local

## Validações

- [x] Digitar 1 letra em Nome/Marca/Modelo dispara consulta e mostra opções
- [x] Valor novo (não listado) continua salvável (`freeSolo`)
- [x] Request sem permissão → 403
- [x] `q` vazio → `items: []`
- [x] Prefixo case-insensitive
- [x] Testes backend/frontend passam

## Resultado

Implementado em 2026-08-06:

- Backend: `GET /inventory/items/suggestions`, service `suggest_item_field_values`, schema `InventoryFieldSuggestionsRead`, migração de índices `0003`.
- Frontend: `Autocomplete freeSolo` em Nome/Marca/Modelo/Categoria/Local, debounce 150 ms, `AbortController`, método `inventoryService.suggestItemField`.
- Testes: `test_item_field_suggestions_prefix_and_distinct`, `inventory-form-suggestions.test.tsx`, cobertura no `inventory-client.test.ts`.
- Deploy: ver `planos/2026-08-06-deploy-autocomplete-cadastro-itens.md`.
