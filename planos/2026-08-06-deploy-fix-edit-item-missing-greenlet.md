# Deploy em produção — correção edição de item (MissingGreenlet)

## Contexto
Usuário autorizou deploy da correção do `PATCH /inventory/items/{id}` que retornava 500 em produção.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`
- Escopo: **somente backend** (frontend sem alteração necessária)

## Etapas
1. Build/push imagem ECR com fix de `flush`+`refresh` em `update_item`.
2. Registrar nova task definition a partir da revisão em produção.
3. Atualizar serviço ECS e aguardar rollout.
4. Validar health e ausência de 500 no endpoint de edição (quando houver uso).

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Imagem ECR | `prod-2026-08-06-fix-edit-item` |
| Task definition | `remobs-inventario-backend:11` |
| ECS rollout | `COMPLETED` (1/1 running) |
| Health | `https://api-inventario.remobs.com.br/healthz` → 200 `{"status":"ok"}` |

### Observações
- Frontend não precisou de deploy (só backend).
- Correção: `flush` + `refresh` em `update_item` antes de serializar `updated_at`.
