# Pré-preencher origem da saída com o local do item

## Contexto

Na tela Solicitar saída, a origem era preenchida com `balances[0]`, sem preferir o **Local** atual do item (`current_location_id`).

## Objetivo

Ao abrir a saída a partir do detalhe (ou ao trocar o item), pré-preencher Origem com o local do item quando houver saldo disponível nesse local.

## Escopo

- `frontend/src/types.ts` — `current_location_id`
- `frontend/src/pages/MovementRequestPage.tsx` — `resolveOriginLocationId`
- Testes e changelog

## Regra

1. Saldo com `location_id === current_location_id` e disponível &gt; 0
2. Senão, primeiro saldo com disponível &gt; 0
3. Senão, `balances[0]`
4. Com `itemId` vindo do detalhe, sempre reaplica a regra (não reusa origem de outro item no rascunho)

## Validação

- Item com local Campo e saldo em Campo → Origem = Campo
- Local atual sem disponível → cai no primeiro com estoque

## Resultado

Implementado e commitado em `fix: pré-preencher origem da saída com o local do item`.
