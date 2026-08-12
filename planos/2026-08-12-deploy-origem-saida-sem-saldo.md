# Deploy em produção — origem da saída sem saldo e reparo de stock_balances

## Contexto
Usuário autorizou:
- reparo dos permanentes ativos sem saldo;
- publicação da correção da origem na saída.

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Cluster: `remobs-inventario-cluster`
- Serviço: `remobs-inventario-backend`
- Amplify: app `d1oidnxd2f4saq`, branch `prod`

## Etapas
1. Aplicar `backend/scripts/repair_missing_stock_balances.py --apply --yes`.
2. Bump PWA cache `remobs-inventario-v11`.
3. Push da `main` para o GitHub.
4. Build/push imagem backend ECR.
5. Registrar task definition e atualizar serviço ECS.
6. Build frontend e deploy Amplify manual.
7. Validar health, `sw.js` e origem preenchida a partir do Local.

## Resultado
Em andamento.
