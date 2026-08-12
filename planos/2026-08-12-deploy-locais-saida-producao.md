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
Em andamento.
