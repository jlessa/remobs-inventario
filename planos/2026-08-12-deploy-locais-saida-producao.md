# Deploy em produção — locais, origem na saída e visualização de imagem

## Contexto
Usuário autorizou publicação em produção das entregas:
- visualizar imagem do item sem download;
- pré-preencher origem da saída com o local do item;
- CRUD de Locais + autocomplete na saída;
- commits anteriores ainda não publicados (CRUD/anexos/S3/autocomplete/snackbar).

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`
- Amplify: app `d1oidnxd2f4saq`, branch `prod`

## Etapas
1. Bump PWA cache `remobs-inventario-v9`.
2. Push da `main` para o GitHub.
3. Build/push imagem backend ECR.
4. Registrar task definition e atualizar serviço ECS.
5. Build frontend e deploy Amplify manual.
6. Registrar permissões `location:*` na role `admin-inventario`.
7. Validar health, OpenAPI `/locations` e frontend.

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Imagem ECR | `prod-2026-08-12-locais-saida` |
| Task definition | `remobs-inventario-backend:12` |
| ECS rollout | `COMPLETED` (1/1 running) |
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `33` `SUCCEED` (job `32` inicial + republicação com fallbacks) |
| PWA cache | `remobs-inventario-v10` |
| Bundle | `index-DYX0ehjL.js` |
| Permissões | 4 novas (`location:read|create|update|delete`) criadas e anexadas à role `admin-inventario` (id 24); catálogo inventário **25/25** |

### Validações
- `https://api-inventario.remobs.com.br/healthz` → 200 `{"status":"ok"}`
- OpenAPI: `/locations` (`get,post`) e `/locations/{location_id}` (`get,patch,delete`)
- `https://inventario.remobs.com.br/` → 200
- `https://inventario.remobs.com.br/app/locations/` → 200
- `https://inventario.remobs.com.br/app/locations/new/` → 200
- `sw.js` com `remobs-inventario-v10`
- Bundle com rota `/app/locations` e texto `Visualizar`

### Observações
- Usuários com role `admin-inventario` precisam **relogin** para carregar as permissões `location:*` no JWT.
- Sem migração de banco no inventário neste deploy (tabela `locations` já existia).
- Fallback SPA de Locais incluído após 404 inicial na rota direta `/app/locations/`.
