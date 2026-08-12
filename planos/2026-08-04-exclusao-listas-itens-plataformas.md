# Exclusão nas listas de itens e plataformas

## Contexto
As listagens de inventário e plataformas não ofereciam ação de exclusão na interface, embora o backend já suportasse soft delete de itens (`DELETE /inventory/items/{id}`).

## Objetivo
Permitir excluir itens e plataformas diretamente nas respectivas listagens, com confirmação e controle por permissão.

## Escopo
- Frontend: `InventoryListPage`, `PlatformsPage`, `inventoryService`
- Backend: endpoint de soft delete de plataformas
- Testes de UI para botões de exclusão

## Etapas
1. Adicionar `DELETE /platforms/{id}` com soft delete e auditoria.
2. Expor `deleteItem` e `deletePlatform` no serviço do frontend.
3. Incluir botão de exclusão nas listas (visível apenas com permissão).
4. Atualizar testes e changelog.

## Resultado
- Itens: botão de excluir com permissão `inventory:item:delete`.
- Plataformas: botão de excluir com permissão `platform:update`.
- Confirmação via `window.confirm` e remoção otimista da lista após sucesso.
