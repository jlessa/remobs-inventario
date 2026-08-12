# Deploy em produção — upload de arquivos/imagens com S3

## Contexto
Usuário autorizou deploy da correção de upload e do bucket S3 `inventario-remobs`.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`

## Etapas
1. Build/push imagem backend com S3 (`boto3` + endpoints de arquivos).
2. Registrar task definition com:
   - `taskRoleArn` = `remobs-inventario-backend-task-role`
   - envs `REMOBS_STORAGE_BACKEND=s3` e bucket `inventario-remobs`
3. Atualizar serviço ECS.
4. Build/deploy frontend (UI de anexos) no Amplify `prod`.
5. Validar health, OpenAPI e presença de rotas de arquivos.

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Imagem ECR | `prod-2026-08-06-s3-files` |
| Task definition | `remobs-inventario-backend:8` |
| Task role | `remobs-inventario-backend-task-role` |
| Storage | `REMOBS_STORAGE_BACKEND=s3` → bucket `inventario-remobs` |
| ECS rollout | `COMPLETED` (1/1 running) |
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `28` `SUCCEED` |
| PWA cache | `remobs-inventario-v5` |

### Validações
- `https://api-inventario.remobs.com.br/healthz` → 200
- OpenAPI com rotas de files (`GET/POST .../files`, `GET .../content`, `DELETE ...`)
- `https://inventario.remobs.com.br/` → 200
- Bundle com “Anexar foto” e path `/files`
- `sw.js` com `remobs-inventario-v5`
