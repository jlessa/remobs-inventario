# Correção — edição de item não salva (500 MissingGreenlet)

## Contexto

Usuário reportou que a funcionalidade de editar item em produção não salva alterações.

## Diagnóstico (produção)

- Log group: `/ecs/remobs-inventario-backend`
- Vários `PATCH /inventory/items/{id}` retornando **500 Internal Server Error**
- Exceção: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called`
- Stack:
  - `app/routers/inventory.py` → `update_item` (serialize after_data)
  - `app/services/inventory_service.py` → `serialize_item` linha `updated_at`
- Causa: após `setattr` no item, a coluna `updated_at` (`onupdate=func.now()`) fica **expirada**; no SQLAlchemy async, ler o atributo dispara lazy load síncrono e gera `MissingGreenlet`.
- Auditoria: zero `inventory_item_updated` com sucesso; creates (`POST`) funcionam (há `flush` antes do serialize).

## Correção

Em `update_item`, após aplicar campos:

1. `await session.flush()`
2. `await session.refresh(item)`
3. só então `serialize_item` / auditoria / commit

Teste: `test_updates_inventory_item_without_missing_greenlet`.

## Deploy

Backend precisa de novo deploy ECS para valer em produção.

## Resultado

Código corrigido e **publicado em produção**.

- Imagem: `prod-2026-08-06-fix-edit-item`
- Task definition: `remobs-inventario-backend:11`
- Rollout: `COMPLETED`
- Detalhes: `planos/2026-08-06-deploy-fix-edit-item-missing-greenlet.md`
