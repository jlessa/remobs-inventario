# Deploy em produção — CRUD completo e permissões granulares

## Contexto
Usuário autorizou deploy do inventário após implementação de CRUD completo (itens, plataformas, sensores, checklists) e registro das permissões na role `admin-inventario`.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`
- Amplify: app `d1oidnxd2f4saq`, branch `prod`

## Etapas
1. Bump PWA cache `remobs-inventario-v8`.
2. Build/push imagem backend ECR.
3. Registrar task definition e atualizar serviço ECS.
4. Build frontend e deploy Amplify manual.
5. Validar health, OpenAPI (delete sensor/checklist) e bundle front.

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Imagem ECR | `prod-2026-08-06-crud-permissions` |
| Task definition | `remobs-inventario-backend:10` |
| ECS rollout | `COMPLETED` (1/1 running) |
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `31` `SUCCEED` |
| PWA cache | `remobs-inventario-v8` |

### Validações
- `https://api-inventario.remobs.com.br/healthz` → 200 `{"status":"ok"}`
- OpenAPI: `/sensors/{sensor_id}` com `get,patch,delete`
- OpenAPI: `/checklists/{checklist_id}` com `get,patch,delete`
- `https://inventario.remobs.com.br/` → 200
- `sw.js` com `remobs-inventario-v8`
- Bundle `index-CHXMKzIr.js` com rotas de edit, textos/permissões CRUD

### Observações
- Permissões já estavam registradas na role `admin-inventario` (id 24) antes do deploy de app.
- Usuários precisam **relogin** para carregar as 8 permissões novas no JWT.
- Sem migração de banco neste deploy (soft delete de sensor e hard delete de checklist usam schema existente).
