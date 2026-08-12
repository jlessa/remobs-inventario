# CRUD de Locais e autocomplete na solicitação de saída

## Contexto

A tabela `locations` já existia (get-or-create), mas sem API/UI de CRUD. Destino na saída era texto livre.

## Objetivo

- CRUD completo de Locais (lista, criar, editar, inativar)
- Autocomplete de origem (saldos do item) e destino (locais ativos) na saída
- Cadastro de item (Local) alimentado pela lista de Locais
- Permissões `location:read|create|update|delete`

## Escopo

- Backend: `schemas/location.py`, `routers/locations.py`, `main.py`, permissões, testes
- Frontend: páginas Locais, rotas, navegação, serviço, `MovementRequestPage`, `InventoryFormPage`

## Validação

- `GET/POST/PATCH/DELETE /locations`
- Menu Locais com listagem e formulário
- Saída: destino sugere locais; origem lista saldos; envia `to_location_id` quando selecionado

## Resultado

Implementado e commitado em `feat: CRUD de locais e autocomplete na solicitação de saída`.
