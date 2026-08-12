# Criar role admin-inventario no controle de usuários (produção)

## Contexto
O inventário REMOBS exige permissões granulares no JWT emitido por pi-controle-usuarios.remobs.com.br.
Era necessário um papel administrativo específico do inventário com o catálogo completo de permissões.

## Objetivo
Criar o role dmin-inventario em produção no emobs-users, com todas as permissões do inventário.

## Escopo
- Ambiente: produção AWS (ws-remobs, região sa-east-1)
- Serviço: cluster ECS emobs-users-cluster / API https://api-controle-usuarios.remobs.com.br
- Banco: RDS do controle de usuários (emobs_users)

## Etapas executadas
1. Localizar catálogo canônico em ackend/scripts/register_inventory_permissions.py.
2. Acessar produção via profile AWS ws-remobs e task definition do ECS.
3. Conectar no banco de produção do controle de usuários (sem expor credenciais).
4. Garantir existência das 13 permissões do inventário.
5. Criar role dmin-inventario e vincular as 13 permissões.

## Resultado
- Role criado: dmin-inventario (id 24)
- Permissões vinculadas (13/13):
  - inventory:item:read
  - inventory:item:create
  - inventory:item:update
  - inventory:item:delete
  - inventory:movement:request
  - inventory:movement:approve
  - platform:read
  - platform:update
  - sensor:read
  - sensor:update
  - checklist:submit
  - udit:log:read
  - sync:write
- Todas as permissões acima foram **criadas** nesta operação (ainda não existiam no banco).

## Observações
- Login HTTP administrativo não foi usado (credenciais de admin local não batem com produção).
- Operação feita via AWS ECS task definition + SQL no RDS de produção.
- Nome normalizado para dmin-inventario (correção ortográfica de "admin-invetario").
- Próximo passo opcional: atribuir o role a usuários no painel emobs-user-front ou via POST /users/{id}/roles.

## Validações
- Query de verificação no banco: role_id 24 possui exatamente as 13 permissões esperadas; missing = [].
