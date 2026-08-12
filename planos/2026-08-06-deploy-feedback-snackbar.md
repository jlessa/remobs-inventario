# Deploy em produção — feedback Snackbar nas ações

## Contexto
Usuário autorizou publicação do feedback visual com Snackbar (sem alteração de backend).

## Ambiente
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Amplify: app `d1oidnxd2f4saq`, branch `prod`

## Etapas
1. Bump PWA cache para `remobs-inventario-v7`.
2. Build do frontend.
3. Deploy manual Amplify.
4. Validar site, `sw.js` e bundle com mensagens de snackbar.

## Resultado
Concluído.

| Item | Valor |
|------|--------|
| Amplify | app `d1oidnxd2f4saq`, branch `prod`, job `30` `SUCCEED` |
| PWA cache | `remobs-inventario-v7` |
| Backend | sem mudança (task `remobs-inventario-backend:9`) |

### Validações
- `https://inventario.remobs.com.br/` → 200
- `sw.js` com `remobs-inventario-v7`
- Bundle com `Foto anexada com sucesso` e código de snackbar
