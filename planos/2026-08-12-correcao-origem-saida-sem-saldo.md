# Correção da origem na saída quando o item não tem saldo

## Contexto

Em produção, a saída do item `bfdf5c9c-d282-4293-85be-b43575dd19e8` (ADCP Nortek Signature 500) não preencheu o local. O item tem **Local** = `Paiol PNBOIA`, mas não possui linhas em `stock_balances`.

A tela Solicitar saída montava a origem só a partir dos saldos. Sem saldo, `resolveOriginLocationId` retornava vazio e o autocomplete ficava em branco.

## Objetivo

- Pré-preencher Origem com o Local do item (`current_location_id`), mesmo sem saldo nesse local.
- Oferecer os locais cadastrados como opções de origem (não só os saldos).
- Criar saldo no local ao cadastrar/editar item, para o caso não se repetir.
- Reparar permanentes ativos sem nenhum saldo, para a saída conseguir ser enviada.

## Escopo

- `frontend/src/pages/MovementRequestPage.tsx`
- `frontend/tests/movement-request-origin.test.tsx`
- `backend/app/routers/inventory.py`
- `backend/tests/test_auth_inventory_contract.py`
- Script de reparo pontual de saldos ausentes

## Validação

- Item com Local e sem balances → Origem = nome do Local.
- Item com Local e saldo em outro local → Origem = Local do item.
- Cadastro com quantidade inicial 0 ainda gera linha de saldo no local.

## Resultado

Corrigido no código: origem usa o Local do item e a lista de Locais, mesmo sem saldo.

Reparo em produção aplicado: **61** permanentes receberam saldo quantidade 1 no local atual; nenhum item ativo ficou sem `stock_balances`.
