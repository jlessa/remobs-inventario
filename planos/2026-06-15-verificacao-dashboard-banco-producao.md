# Plano de execução - Verificação do dashboard e dados de produção

## Contexto

O usuário informou que o dashboard de produção continua exibindo apenas os indicadores atuais, sem refletir checklists, e pediu para verificar o banco e outras telas para confirmar se o problema está no frontend.

## Objetivo

Identificar se a divergência vem do frontend, da API ou dos dados persistidos no banco de produção, corrigindo o dashboard quando houver falha de consumo dos dados já disponíveis.

## Escopo

- Verificar o fluxo de dados usado pelo dashboard.
- Adicionar indicadores de checklists no dashboard.
- Criar teste automatizado para validar a consulta e exibição de checklists.
- Preparar verificação segura do banco/API de produção sem expor segredos.
- Atualizar o changelog.

## Fora do escopo

- Importar planilhas para o banco de produção sem confirmação explícita separada.
- Criar, alterar ou apagar dados de produção durante a etapa de diagnóstico.
- Executar comandos AWS sem confirmação prévia do usuário.

## Etapas

1. Confirmar a origem dos indicadores exibidos no dashboard.
2. Criar teste que falhe enquanto o dashboard não carregar checklists.
3. Implementar a consulta e os cards de checklists no dashboard.
4. Executar testes e build do frontend.
5. Verificar outras telas por inspeção de rotas e serviços.
6. Confirmar comandos AWS planejados antes de consultar banco/produção.
7. Registrar resultado e evidências.

## Resultado

Concluído.

Foi identificada uma falha objetiva no frontend: o dashboard carregava itens, movimentações, alertas, plataformas, sensores e sincronização, mas não chamava o endpoint `/checklists`. Por isso, checklists nunca apareceriam nos indicadores do dashboard, mesmo que existissem no banco.

A tela de lista de checklists já usa `inventoryService.listChecklists()`, e as telas de inventário, plataformas e sensores já usam seus respectivos endpoints de listagem. A divergência encontrada até aqui é específica do dashboard.

Correção local implementada:

- Inclusão de `inventoryService.listChecklists()` no carregamento do dashboard.
- Inclusão dos cards `Checklists registrados` e `Checklists enviados`.
- Tratamento defensivo para não derrubar todos os indicadores caso o usuário não tenha permissão de checklist.

Validações locais executadas:

- `npm test -- dashboard-checklists.test.tsx --run`: 1 teste aprovado.
- `npm test -- --run`: 9 arquivos de teste e 18 testes aprovados.
- `npm run build`: build concluído com sucesso, gerando o bundle `assets/index-CnNCno9r.js`.

Validações de produção após o deploy:

- AWS Amplify app `d1oidnxd2f4saq`, branch `prod`, job `20`: `SUCCEED`.
- Passos do job `20`: `DEPLOY` e `VERIFY` concluídos com sucesso.
- `https://inventario.remobs.com.br/login/?v=20`: HTTP 200.
- `https://inventario.remobs.com.br/app/home/?v=20`: HTTP 200.
- HTML de produção apontando para `/assets/index-CnNCno9r.js`.
- Bundle publicado contém `Checklists registrados`, `Checklists enviados` e a chamada `listChecklists`.
- `sw.js` publicado contém `remobs-inventario-v2`, `skipWaiting` e `clients.claim`.

Verificação read-only executada no banco de produção a partir da task ativa do ECS:

- Conta AWS: `220790920077`.
- Cluster ECS: `api-controle-usuarios-prod-cluster`.
- Serviço ECS: `remobs-inventario-backend`.
- Task definition ativa: `remobs-inventario-backend:3`.
- `desired_count`: 1.
- `running_count`: 1.
- Alembic: `0002_add_field_checklists`.
- Tabela `field_checklists`: presente.
- Itens ativos: 1.
- Itens totais: 4, sendo 3 removidos logicamente.
- Estoque total agregado: 6.
- Estoque crítico: 0.
- Movimentações pendentes: 0.
- Plataformas: 0.
- Sensores: 0.
- Checklists: 0.
- Alertas abertos: 0.
- Ações offline: 0.

Conclusão parcial:

- O valor `Itens cadastrados = 1` do dashboard está coerente com o banco de produção.
- O dashboard não exibia checklists por falha de frontend, pois não consultava `/checklists`.
- Mesmo após corrigir o frontend, o indicador de checklists retornará `0` enquanto não houver checklists criados no banco de produção.
- As telas de inventário, plataformas, sensores e checklists usam os endpoints de listagem corretos; a ausência de plataformas, sensores e checklists é coerente com os dados atuais do banco.
