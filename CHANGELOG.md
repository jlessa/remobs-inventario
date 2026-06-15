# CHANGELOG

## [2026-06-15]

### Adicionado
- Checklist de campo detalhado no frontend, com seções para operação, condições ambientais, equipe, embarcações, fotografias obrigatórias, inspeção técnica, problemas, solução e pós-campo.
- Exibição agrupada das respostas do checklist na tela de detalhe, com rótulos legíveis e valores booleanos apresentados como `Sim` ou `Não`.
- Teste automatizado para validar o preenchimento do checklist de campo detalhado e o payload enviado ao serviço de checklists.

### Analisado
- Análise das planilhas em `docs/` para identificar oportunidades de evolução do sistema de inventário, incluindo importação assistida de itens, estações, pendências, checklists de campo, ferramentas e catálogos auxiliares.

### Observado
- Foram registradas lacunas de saneamento nos dados das planilhas, incluindo quantidades ausentes no paiol, baixa cobertura de condição e movimentação no inventário de laboratório, duplicidades de série/TAG, contatos pouco estruturados e fórmulas de pendências que retornam erro quando lidas como valor calculado.

## [2026-06-09]

### Adicionado
- Formulários no frontend para cadastrar plataformas e sensores, com envio para os endpoints operacionais existentes.
- Botões de ação nas páginas de plataformas e sensores para usuários com permissões `platform:update` e `sensor:update`.
- Testes automatizados para validar a presença das ações de cadastro e o uso dos endpoints `POST /platforms` e `POST /sensors`.

### Corrigido
- Correção da ausência do fluxo de cadastro de plataformas e sensores no frontend.

### Publicado
- Publicação manual do frontend atualizado no AWS Amplify de produção, branch `prod`, usando o perfil AWS `aws-remobs`.

## [2026-06-08]

### Adicionado
- Backend FastAPI em `backend/`, com configuração por variáveis `REMOBS_*`, CORS, healthcheck, erro padronizado, SQLAlchemy assíncrono, autenticação JWT local compatível com `remobs-users` e autorização por permissões.
- Modelos, schemas, serviços e rotas iniciais para inventário, saldos, movimentações, auditoria, alertas, plataformas, sensores, arquivos/metadados e sincronização offline.
- Migração Alembic inicial para criação das tabelas principais no banco PostgreSQL dedicado, usando o schema padrão `public`, sem execução automática no RDS.
- Script auxiliar para registrar permissões do inventário no backend de usuários.
- Frontend React + TypeScript + Material UI em `frontend/`, com PWA básico, login integrado ao backend de usuários, rotas protegidas, layout mobile-first, navegação por permissão, inventário, movimentações, alertas, plataformas, sensores, checklists e sincronização.
- Ambiente de produção do frontend configurado para usar o autenticador em `https://api-controle-usuarios.remobs.com.br`.
- Testes automatizados de backend para JWT, permissões, inventário, movimentações e auditoria.
- Teste automatizado de frontend para navegação por permissão.
- Testes automatizados de frontend para configuração das APIs e resolução da URL completa do login.
- Plano de produção AWS para ECS/Fargate, ECR, Amplify, banco dedicado no RDS existente, load balancer já implementado e DNS `inventario.remobs.com.br`.
- Dockerfile e `.dockerignore` do backend para publicação em ECS/Fargate.
- Build spec `amplify.yml` para deploy do frontend no AWS Amplify usando o diretório `frontend/`.
- Configuração de produção do frontend para apontar a API de inventário para `https://api-inventario.remobs.com.br`.
- Recursos AWS iniciais de produção: repositório ECR `remobs-inventario-backend`, imagem publicada com tags `prod-2026-06-08-inicial` e `latest`, security group da task, target group, log group, certificado ACM validado e regra HTTPS no load balancer existente.
- Scripts de provisionamento do banco dedicado do inventário a partir das configurações existentes do ECS, sem imprimir segredos.
- Provisionamento do banco dedicado `remobs_inventario` no RDS existente e do usuário `remobs_inventario_app`, validado por conexão real e criação/remoção de tabela de teste.
- Nova imagem `prod-2026-06-08-banco` publicada no ECR e task definition `remobs-inventario-backend:2` registrado com `REMOBS_DATABASE_SSL=require`.
- Serviço ECS/Fargate `remobs-inventario-backend` criado no cluster existente, com target group saudável no load balancer compartilhado.
- Registros DNS públicos criados para `api-inventario.remobs.com.br` e `inventario.remobs.com.br`.
- App AWS Amplify `remobs-inventario-frontend` criado e publicado na branch `prod`.
- Script `backend/scripts/smoke_production.py` para validação autenticada de produção sem registrar token ou credenciais no código.
- Script `frontend/scripts/create-spa-fallbacks.mjs` para gerar fallbacks estáticos das rotas do SPA no artefato do Amplify.
- Contratos backend e telas frontend para checklists de campo, detalhe de plataforma, detalhe de sensor e resolução de conflitos offline.
- Dashboard operacional completo com indicadores de estoque crítico, plataformas, sensores, solicitações pendentes e sincronização.
- Inventário com busca, filtros rápidos, cadastro ampliado, detalhe técnico e histórico.
- Solicitação de saída com validação de estoque, seleção de origem, rascunho local e confirmação antes do envio.

### Alterado
- Atualização da configuração local do ecossistema para os caminhos reais disponíveis no ambiente de desenvolvimento atual.
- Atualização do `.gitignore` para ignorar artefatos Python e bancos SQLite locais de teste.
- Centralização da configuração de URLs das APIs do frontend, com normalização de barras finais e fallback seguro para o autenticador de produção.
- Configuração de fallback local para a API do inventário em `http://127.0.0.1:8000`, evitando chamadas acidentais à própria origem do Vite.
- Ajuste do plano de produção AWS para não criar schema dedicado, não criar novo load balancer, não criar novo RDS e restringir custos novos a ECS/Fargate, ECR e Amplify.
- Ajuste do backend e da migration inicial para usar banco PostgreSQL dedicado com schema padrão `public`, sem criação do schema `inventario`.
- Suporte do backend à variável `REMOBS_DATABASE_SSL=require` para conexão PostgreSQL criptografada em produção.
- Ajuste do `alembic.ini` para resolver caminhos a partir do próprio arquivo, permitindo execução local e no container.
- Publicação do backend em ECS usando o banco dedicado `remobs_inventario` e o usuário próprio `remobs_inventario_app`.
- Ajuste da tela de login para declarar autocomplete de usuário e senha.
- Remoção do planejamento de telas administrativas e de recuperação de senha da documentação operacional do inventário.

### Corrigido
- Correção do login do frontend para evitar chamadas para a própria origem do Vite, garantindo o uso de `https://api-controle-usuarios.remobs.com.br/auth/login`.
- Correção da URL padrão do cliente de inventário para impedir que rotas como `/inventory/items` sejam resolvidas em `http://127.0.0.1:5173`.
- Correção das rotas diretas do frontend no Amplify, incluindo `/login/`, `/app/home/` e `/app/inventory/`, por meio de fallbacks estáticos do SPA.
- Correção do `404` de favicon na aplicação publicada.

### Observado
- A regra temporária de acesso ao RDS pelo IP local foi removida ao final do provisionamento.
- A migration inicial foi executada no banco dedicado após autorização do usuário e validada pela presença das tabelas esperadas.
- O frontend publicado foi validado em navegador real nos viewports 360px, 390px, 430px e 1440px, sem erros ou warnings de console.
- O smoke test de produção validou login, `/users/me`, inventário, criação e remoção de item de teste, histórico, movimentação rejeitada, auditoria, alertas, plataformas, sensores e sync.

## [2026-06-03]

### Adicionado
- Download de todas as 25 telas do Google Stitch (mobile, desktop e assets) no diretório local `telas/` em formato HTML/SVG.
- Criação do arquivo de configurações reais `.config` e do modelo de referência `.config.example` com o mapeamento de caminhos do ecossistema REMOBS.
- Criação do arquivo de diretrizes operacionais `AGENTS.md` em português do Brasil, contendo as instruções do projeto, diretrizes Clean Code, padrões de desenvolvimento e uma tabela dinâmica referenciando todas as 25 telas locais com links clicáveis e seus Stitch IDs correspondentes.
- Geração das versões desktop de todas as 10 telas funcionais (Lista de Inventário, Dashboard, Login, Solicitar Saída, Detalhes do Sensor, Adicionar Item, Detalhes da Plataforma, Field Checklist, Offline Sync e Audit Logs) no projeto Stitch `15941217647782050586`, seguindo layouts responsivos com sidebars, grids de 12 colunas, visualização master-detail e tabelas de dados.
- Geração das 3 telas mobile restantes (Field Checklist Form, Offline Sync and Conflict Resolution, e Audit Logs) no projeto Stitch.
