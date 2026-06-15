# Correção do dashboard em produção

## Contexto

Em 15/06/2026, a tela `https://inventario.remobs.com.br/app/home/` continuou exibindo os cartões do dashboard com valores zerados, apesar de a validação read-only do banco de produção indicar dados importados.

As evidências coletadas em produção mostram:

- O frontend publicado carrega o bundle atual e aponta para `https://api-inventario.remobs.com.br`.
- O serviço ECS `remobs-inventario-backend` está ativo em produção.
- O banco de produção possui os dados importados.
- Após a carga, os logs mostram respostas `200 OK` para plataformas, sensores, checklists, alertas e sincronização.
- O endpoint `GET /inventory/items` deixou de concluir nas navegações reais do dashboard após a carga maior de itens.

## Objetivo

Corrigir a tela inicial para exibir os indicadores a partir de um resumo agregado calculado no backend, sem depender da listagem completa de itens do inventário.

## Escopo

- Criar contrato de resumo do dashboard no backend.
- Calcular indicadores por consultas agregadas no banco.
- Trocar a home do frontend para consumir o resumo.
- Manter os cartões e listas resumidas da tela inicial.
- Validar por testes automatizados de backend e frontend.

## Fora de escopo

- Alterar credenciais, banco, DNS ou infraestrutura persistente.
- Executar migrações de banco.
- Refatorar a listagem completa de inventário.

## Etapas

1. Registrar teste de backend para o novo resumo agregado.
2. Registrar teste de frontend para a home consumir o resumo do dashboard.
3. Implementar rota agregada no backend.
4. Atualizar serviço e tela inicial no frontend.
5. Executar testes e build local.
6. Atualizar changelog.
7. Solicitar confirmação antes de commit, push e deploy.

## Validações

- `python -m pytest`
- `npm test -- --run`
- `npm run build`

## Resultado

Implementação local concluída e validada.

Foi criado o endpoint `GET /dashboard/summary` no backend para calcular os indicadores diretamente no banco PostgreSQL. A tela inicial passou a consumir esse resumo agregado por `inventoryService.getDashboardSummary()`, sem depender de `GET /inventory/items` para montar os cartões.

Validações executadas:

- `python -m pytest backend\tests\test_auth_inventory_contract.py::test_dashboard_summary_returns_aggregated_operational_counts`: 1 teste aprovado.
- `npm test -- --run tests/dashboard-checklists.test.tsx`: 1 teste aprovado.
- `python -m pytest` no backend: 12 testes aprovados.
- `npm test -- --run` no frontend: 9 arquivos de teste e 18 testes aprovados.
- `npm run build` no frontend: build concluído com sucesso.

Commit, push e deploy em produção ainda dependem de confirmação explícita do usuário.
