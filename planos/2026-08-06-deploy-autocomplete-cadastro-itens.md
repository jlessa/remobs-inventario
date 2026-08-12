# Deploy em produção — autocomplete no cadastro de itens

## Contexto
Usuário autorizou extensão de autocomplete (categoria/local) e deploy em produção.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`
- Amplify: app `d1oidnxd2f4saq`, branch `prod`

## Etapas
1. Testes locais backend/frontend.
2. Migração Alembic `0003` (índices brand/model) via task definition.
3. Build/push imagem backend ECR.
4. Registrar task definition e atualizar serviço ECS.
5. Build frontend + bump PWA `remobs-inventario-v6`.
6. Deploy Amplify manual.
7. Validar health, OpenAPI `/suggestions` e bundle front.

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Imagem ECR | `prod-2026-08-06-autocomplete` |
| Task definition | `remobs-inventario-backend:9` |
| Migração | `0003_item_brand_model_idx` (índices brand/model) |
| ECS rollout | `COMPLETED` (1/1 running) |
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `29` `SUCCEED` |
| PWA cache | `remobs-inventario-v6` |

### Validações
- `https://api-inventario.remobs.com.br/healthz` → 200
- OpenAPI com `/inventory/items/suggestions`
- `https://inventario.remobs.com.br/` → 200
- Bundle com `suggestions` e `category_name`
- `sw.js` com `remobs-inventario-v6`

### Nota
Revision Alembic inicial `0003_index_inventory_item_brand_model` excedia `varchar(32)` de `alembic_version`; renomeada para `0003_item_brand_model_idx`.
