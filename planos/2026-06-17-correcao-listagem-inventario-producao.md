# Correção da listagem de inventário em produção (consultas N+1)

## Contexto

Após a carga das planilhas em produção (728 itens de inventário, 113 plataformas, 218 sensores e 12 checklists), as telas do sistema deixaram de exibir os itens. A investigação confirmou que o backend e o banco de produção estavam saudáveis e com os dados carregados, mas o endpoint de listagem de inventário não respondia em tempo hábil.

## Objetivo

Restabelecer a renderização dos itens nas telas de produção, corrigindo a causa raiz da indisponibilidade do endpoint `GET /inventory/items`.

## Diagnóstico

- API de produção saudável: `healthz` 200; endpoints autenticados respondendo.
- Banco de produção com dados: `/dashboard/summary`, `/platforms`, `/sensors` e `/checklists` retornaram 200 rapidamente.
- Apenas `GET /inventory/items` excedia 60 segundos (timeout), com token válido e permissões `*`.
- Causa raiz: a serialização da lista chamava `serialize_item` item a item, e cada item disparava consultas adicionais (categoria, local atual e saldos). Com 728 itens, isso gerava aproximadamente 2.184 idas e voltas sequenciais ao RDS, ultrapassando o tempo limite do balanceador e do cliente.
- O ambiente local com SQLite não reproduzia o problema porque a latência por consulta é praticamente nula; em produção, com o RDS remoto, o custo por ida e volta tornou a listagem inviável.

## Escopo

- `backend/app/services/inventory_service.py`: nova função `serialize_items_bulk`, que carrega categorias, locais atuais e saldos em lote (número fixo de consultas, independente da quantidade de itens) e monta a resposta em memória, preservando o mesmo formato de `serialize_item`.
- `backend/app/routers/inventory.py`: o endpoint de listagem passa a usar `serialize_items_bulk`.
- `backend/scripts/check_production_readonly.py`: script de validação somente leitura da produção (login e contagem por endpoint), sem registrar token ou credenciais.

## Validação

- Local (banco com os 728 itens importados): `GET /inventory/items` retornou 728 itens em cerca de 0,13 s, com formato idêntico ao anterior. Suíte de testes do backend: 12 aprovados.
- Produção, após publicação: `GET /inventory/items` retornou 729 em regime estável de aproximadamente 1 s (primeira chamada com cold start do contêiner novo). Demais endpoints permaneceram 200.

## Publicação

- Imagem `prod-2026-06-17-listagem` publicada no ECR `remobs-inventario-backend`.
- Revisão `remobs-inventario-backend:5` registrada a partir da revisão ativa `:4`, preservando variáveis de ambiente e a conexão criptografada do RDS.
- Serviço ECS `remobs-inventario-backend` (cluster `remobs-inventario-cluster`) atualizado com `--force-new-deployment` e estabilizado.
- Frontend republicado no AWS Amplify (aplicativo de inventário, branch `prod`) para usar o resumo agregado do dashboard.
- Profile AWS utilizado: `aws-remobs`. Região: `sa-east-1`.

## Resultado

Listagem de inventário e demais telas voltaram a renderizar os itens em produção.
