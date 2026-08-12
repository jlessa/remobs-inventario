# Plano: Feedback visual com Snackbar nas ações

## Contexto
Ações do sistema usavam `Alert` embutido na página (quando usavam) e, em vários fluxos, não havia confirmação de sucesso. Caso relatado: anexar foto no detalhe do item sem feedback de sucesso ou falha.

## Objetivo
Padronizar feedback de ações mutáveis com Snackbar global (sucesso e erro).

## Abordagem
1. Criar `SnackbarProvider` + `useSnackbar` em `frontend/src/state/SnackbarContext.tsx`.
2. Montar o provider no `main.tsx` (acima de `App`), com posição acima da bottom navigation no mobile.
3. Substituir estados locais de `actionError`/`fileError`/`message` de mutações por snackbar.
4. Manter `Alert` apenas para estados de carregamento/vazio da tela (não ações).
5. Testes de sucesso/erro no upload de anexos.

## Escopo de ações com snackbar
- Anexos: upload, download, remoção
- Inventário: criar item, excluir item
- Plataforma: criar, excluir
- Sensor: criar, registrar inconsistência
- Movimentações: solicitar, aprovar, reprovar
- Checklist: enviar, rascunho local
- Sync: resolver conflito

## Resultado
Implementado em 2026-08-06:

- `SnackbarProvider` global com `showSuccess` / `showError` / `showInfo` / `showWarning`.
- Ações mutáveis das telas principais passam a usar snackbar.
- Testes de anexo cobrem sucesso e falha com snackbar.
- Erros/estados de carregamento de listagem continuam com `Alert` de página.
