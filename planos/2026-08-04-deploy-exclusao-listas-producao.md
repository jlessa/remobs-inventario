# Deploy em produção — exclusão nas listas de itens e plataformas

## Contexto
O usuário autorizou a publicação em produção das alterações de exclusão nas listagens de inventário e plataformas.

## Objetivo
Publicar backend (ECS) e frontend (Amplify) em produção e validar disponibilidade.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`

## Etapas executadas
1. Build e push da imagem Docker do backend para o ECR.
2. Registro da task definition `remobs-inventario-backend:6`.
3. Atualização do serviço ECS `remobs-inventario-backend`.
4. Build do frontend e deploy manual no Amplify (`prod`).
5. Atualização do cache PWA para `remobs-inventario-v3`.
6. Validação de saúde e presença dos artefatos.

## Resultado
- Imagem: `220790920077.dkr.ecr.sa-east-1.amazonaws.com/remobs-inventario-backend:prod-2026-08-04-delete-lists`
- Task definition: `remobs-inventario-backend:6` (rollout `COMPLETED`, 1/1 running)
- Amplify app: `d1oidnxd2f4saq`, job `25`, status `SUCCEED`
- `https://api-inventario.remobs.com.br/healthz` → 200
- `https://inventario.remobs.com.br/` e rotas `/app/inventory/`, `/app/platforms/` → 200
- OpenAPI com métodos `get,patch,delete` em `/platforms/{platform_id}`
- Bundle `index-39K5Rg-Q.js` contém textos de exclusão de item e plataforma
- `sw.js` com `remobs-inventario-v3`
