# CRUD completo em cadastros e permissões

## Contexto

O inventário REMOBS já tem backend parcial e catálogo de 13 permissões em `backend/scripts/register_inventory_permissions.py`, com role `admin-inventario` em produção (plano `2026-08-04-criar-role-admin-inventario-producao.md`).

O pedido atual: **todas as ações de CRUD** em todos os itens e cadastros, com permissões novas se necessário e vínculo às roles no sistema de permissões (`remobs-users` / painel de usuários).

## Diagnóstico (estado atual)

### Backend — endpoints e permissões

| Cadastro | Read | Create | Update | Delete | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Itens inventário | `inventory:item:read` | `create` | `update` | `delete` | CRUD API completo |
| Plataformas | `platform:read` | `platform:update` | `platform:update` | `platform:update` | create/delete reutilizam update |
| Sensores | `sensor:read` | `sensor:update` | `sensor:update` | **ausente** | sem `DELETE /sensors/{id}` |
| Checklists | tudo via `checklist:submit` | mesmo | mesmo | **ausente** | sem delete; list/get exigem submit |
| Movimentos | via `item:read` | `movement:request` | approve/reject | N/A | fluxo operacional, não CRUD puro |
| Auditoria | `audit:log:read` | N/A | N/A | N/A | só leitura |
| Sync | read parcial + `sync:write` | — | — | — | operacional |

### Frontend — UI

| Cadastro | Listar | Criar | Editar formulário | Excluir |
| :--- | :--- | :--- | :--- | :--- |
| Itens | sim | sim | **não** (só anexos no detalhe) | sim (lista) |
| Plataformas | sim | sim | **não** | sim (lista, perm `platform:update`) |
| Sensores | sim | sim | **não** (só “registrar inconsistência”) | **não** |
| Checklists | sim | sim | parcial (formulário/detalhe) | **não** |
| Movimentos | sim | solicitar | aprovar/reprovar | N/A |

Lacunas de rota: não há `/inventory/:id/edit`, `/platforms/:id/edit`, `/sensors/:id/edit`.  
Cliente frontend sem `updateItem`, `updatePlatform`, `deleteSensor`, `deleteChecklist`.

### Sistema de permissões

- Catálogo inventário: script `register_inventory_permissions.py` (não no seed base do `remobs-users`).
- Role produção: `admin-inventario` com as 13 permissões atuais.
- Paths locais reais: `C:\Users\remob\Desktop\desenvolvimento\remobs-users` (o `.config` do inventário ainda aponta para paths de outra máquina — fora deste plano, mas relevante para agentes).

## Objetivo

1. Completar CRUD de API e UI para cadastros principais: **itens, plataformas, sensores, checklists**.
2. Normalizar catálogo de permissões com códigos granulares `resource:action`.
3. Registrar permissões no `remobs-users` e anexar à role `admin-inventario` (e documentar como anexar a outras roles).
4. Gate de UI/backend alinhado (botões e rotas só com permissão).

## Decisão de modelo de permissões (proposta)

Expandir catálogo mantendo códigos existentes e adicionando os que faltam:

### Manter

- `inventory:item:read|create|update|delete`
- `inventory:movement:request|approve`
- `platform:read`
- `sensor:read`
- `checklist:submit`
- `audit:log:read`
- `sync:write`

### Adicionar

- `platform:create`, `platform:delete` (hoje create/delete usam `platform:update`)
- `sensor:create`, `sensor:delete` (hoje create usa `sensor:update`; delete não existe)
- `checklist:read`, `checklist:create`, `checklist:update`, `checklist:delete`
  - `checklist:submit` permanece só para envio final
  - list/get passam a exigir `checklist:read` (com compatibilidade temporária opcional: aceitar `checklist:submit` OU `checklist:read` na transição)

### Compatibilidade

- Backend: create plataforma passa a exigir `platform:create` (não mais `platform:update`).
- Delete plataforma: `platform:delete`.
- Create sensor: `sensor:create`.
- Roles existentes em produção precisam receber os novos códigos **antes** ou **junto** do deploy do backend, senão create/delete quebram para quem só tem `*:update`.

**Mitigação recomendada:** no backend, por 1 versão, aceitar legado:

- create platform: `platform:create` **ou** `platform:update`
- delete platform: `platform:delete` **ou** `platform:update`
- create sensor: `sensor:create` **ou** `sensor:update`

Frontend usa os códigos novos; se usuário só tiver legado, botões de create/delete ainda aparecem via fallback `update` (espelhando regra do backend).

## Escopo de implementação

### A. Backend (`remobs-inventario`)

1. Catálogo em `register_inventory_permissions.py` + descrições pt-BR.
2. `DELETE /sensors/{id}` soft delete + auditoria (espelhar plataformas).
3. `DELETE /checklists/{id}` (rascunhos; política para submitted a definir — default: só draft, ou soft/hard com reason).
4. Ajustar `require_permissions` nos routers (create/delete granulares + compat legado).
5. Checklist: `read` em list/get; `create`/`update`/`submit`/`delete` nos respectivos endpoints.
6. Testes de contrato de permissões.

### B. Frontend (`remobs-inventario`)

1. Serviço: `updateItem`, `updatePlatform`, `deleteSensor`, `deleteChecklist` (+ tipos).
2. Rotas de edição: `.../:id/edit` para item, plataforma, sensor.
3. Formulários em modo create/edit (reuso das FormPages).
4. Detalhe: botões Editar / Excluir com gate de permissão.
5. Listas: create/delete com permissões corretas (sensores e checklists).
6. Checklist list: gate create; delete se permitido.
7. Testes de UI mínimos.

### C. Permissões / roles (`remobs-users` + produção)

1. Script/atualização para registrar permissões novas (API `POST /permissions` ou SQL controlado).
2. Anexar todas as permissões do inventário à role `admin-inventario`.
3. Documentar no plano/changelog como anexar a outras roles via painel `remobs-user-front`.
4. **Não** alterar seed base do dashboard (boias/mare) sem necessidade — inventário continua via script dedicado.

### D. Documentação

1. Atualizar este plano durante a execução.
2. `CHANGELOG.md` do inventário (e de `remobs-permissoes` se houver doc de alinhamento).
3. Opcional: doc em `remobs-permissoes` com matriz de permissões do inventário.

## Fora de escopo (salvo pedido explícito)

- CRUD de cascos/sistemas aninhados como entidades independentes (hoje embutidos no detalhe da plataforma).
- CRUD de usuários/roles no inventário (fica no `remobs-user-front`).
- Tela de auditoria full se ainda não estiver no menu (só perm `audit:log:read`).
- Movimentos: manter fluxo request/approve (não “CRUD genérico”).

## Etapas de execução

1. Confirmar decisões com usuário (granularidade, compat legado, política delete checklist, deploy produção).
2. Implementar backend (endpoints + perms + testes).
3. Implementar frontend (forms edit + delete + gates).
4. Atualizar script de permissões e plano de anexar role.
5. Validar testes locais.
6. Changelog + revisão.
7. **Com confirmação:** registrar permissões e atualizar role em produção.

## Validações

- Testes backend de permissão por endpoint.
- Testes frontend de botões create/edit/delete.
- Matriz: usuário só `read` não vê botões de escrita.
- Role `admin-inventario` com catálogo completo após registro.

## Resultado esperado

Operador com role adequada consegue criar, ler, editar e excluir itens, plataformas, sensores e checklists (conforme política), com permissões explícitas no JWT e botões coerentes na UI.

## Decisões confirmadas (2026-08-06)

1. Modelo: **granular + compat legado** (create/delete aceitam códigos novos ou `*:update` / `checklist:submit`).
2. Escopo: código local + **registro em produção** e anexar à role `admin-inventario`.
3. Checklist: exclusão de **qualquer status** com `reason` obrigatório (hard delete + auditoria).

## Execução (código)

### Backend
- `require_any_permission` em `app/core/permissions.py`.
- Plataformas: create/delete com perms granulares + legado.
- Sensores: create/delete (novo endpoint) com perms granulares + legado.
- Checklists: read/create/update/delete/submit com perms + legado; delete hard com reason.
- Catálogo em `register_inventory_permissions.py` (21 códigos) + anexar role.
- Testes de contrato adicionados (4 novos).

### Frontend
- Service: `updateItem`, `updatePlatform`, `deleteSensor`, `deleteChecklist`.
- Forms em modo create/edit; rotas `.../:id/edit`.
- Detalhes e listas com Editar/Excluir e `hasAnyPermission` para legado.
- Menu checklists: `checklist:read | checklist:submit`.

### Validações
- Frontend: 26 testes OK.
- Backend: 4 testes novos OK (pytest encerrou com hang residual de engine SQLite no Windows; asserções passaram).

## Registro em produção

### Executado em 2026-08-06

- Profile AWS: `aws-remobs` / região `sa-east-1`
- Cluster: `remobs-users-cluster` / service `api-controle-usuarios-prod-service`
- Banco: `remobs_users` (via `REMOBS_DATABASE_URL` da task definition; sem expor credenciais)
- Role: `admin-inventario` (id **24**, já existia)
- Permissões criadas agora: **8** (`platform:create|delete`, `sensor:create|delete`, `checklist:read|create|update|delete`)
- Permissões já existentes atualizadas (descrição): **13**
- Vínculos novos em `role_permissions`: **8**
- Total de permissões do inventário na role: **21/21**
- `missing=[]`

### Catálogo completo na role

`audit:log:read`, `checklist:create|delete|read|submit|update`, `inventory:item:create|delete|read|update`, `inventory:movement:approve|request`, `platform:create|delete|read|update`, `sensor:create|delete|read|update`, `sync:write`

### Método alternativo (API)

`python backend/scripts/register_inventory_permissions.py --auth-api https://api-controle-usuarios.remobs.com.br --token <admin> --role-name admin-inventario`

### Pendente pós-código

- Deploy do backend inventário (endpoints delete sensor/checklist + gates granulares)
- Deploy do frontend (forms edit + botões CRUD)
- Usuários com role `admin-inventario` precisam **relogin** para JWT carregar permissões novas

