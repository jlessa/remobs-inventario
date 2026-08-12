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
Concluído.

| Item | Valor |
|------|--------|
| Reparo de saldos | **61** permanentes, 0 restantes sem `stock_balances` |
| Imagem ECR | `prod-2026-08-12-origem-saida` |
| Task definition | `remobs-inventario-backend:13` |
| ECS rollout | `COMPLETED` (1/1 running) |
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `34` `SUCCEED` |
| PWA cache | `remobs-inventario-v11` |
| Bundle | `index-tCezYMh_.js` |

### Validações
- `https://api-inventario.remobs.com.br/healthz` → 200 `{"status":"ok"}`
- `https://inventario.remobs.com.br/` → 200
- `sw.js` com `remobs-inventario-v11`
- Bundle com preenchimento da origem a partir do Local do item

### Observações
- Faça um recarregamento completo (ou relogin) para o PWA trocar o cache `v10` → `v11`.
- O ADCP `bfdf5c9c-d282-4293-85be-b43575dd19e8` agora tem saldo 1 em Paiol PNBOIA; a origem da saída deve vir preenchida com esse local.
