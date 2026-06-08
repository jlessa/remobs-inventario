# Implementação inicial do backend e frontend

## Contexto

O repositório possuía planos, telas de referência e diretrizes operacionais, mas ainda não continha a aplicação executável. A implementação deve criar backend e frontend no próprio repositório, integrando-se ao backend de usuários já existente para login, JWT e permissões.

No ambiente atual, o projeto dedicado de permissões não foi encontrado. As permissões estão centralizadas no projeto de usuários; por isso, a configuração local aponta o caminho de permissões para o projeto que efetivamente mantém esses dados.

## Objetivo

Criar uma primeira versão funcional do sistema REMOBS Inventário, com API FastAPI, frontend React TypeScript com Material UI, autenticação por JWT compartilhado, estrutura de banco por migrações Alembic e telas operacionais mobile-first.

## Escopo

- Corrigir a configuração local do ecossistema.
- Criar a base do backend com FastAPI, SQLAlchemy assíncrono, Alembic, autenticação JWT, autorização por permissões e erro padronizado.
- Criar entidades iniciais de inventário, movimentações, auditoria, alertas, plataformas, sensores e sincronização.
- Criar frontend com login integrado ao backend de usuários, navegação protegida, layout responsivo, inventário, movimentações, alertas, logs, plataformas, sensores e sincronização.
- Adicionar testes automatizados de backend e frontend.
- Não executar migrações no RDS sem confirmação explícita.

## Etapas

1. Criar testes de contrato para autenticação, permissões, inventário, movimentações e navegação por permissão.
2. Criar a estrutura do backend e implementar o mínimo necessário para os testes passarem.
3. Criar a estrutura do frontend e implementar as telas iniciais.
4. Adicionar migração inicial do schema do inventário.
5. Validar build e testes.
6. Atualizar o changelog com o resultado final.

## Validações

- `python -m pytest backend/tests`
- `npm test -- --run`
- `npm run build`

## Resultado

Concluído nesta etapa inicial.

Foram criados:

- Backend FastAPI em `backend/`, com autenticação JWT compartilhada, autorização por permissões, erro padronizado, inventário, movimentações, auditoria, alertas, plataformas, sensores e sincronização.
- Migração inicial Alembic para o schema `inventario`, sem execução automática no RDS.
- Frontend React TypeScript em `frontend/`, com Material UI, PWA básico, login integrado ao backend de usuários, navegação por permissão e telas operacionais iniciais.
- Script auxiliar para registrar permissões do inventário no backend de usuários.
- Testes automatizados de backend e frontend.
- Ambiente de produção do frontend apontando o autenticador para `https://api-controle-usuarios.remobs.com.br`.

Validações executadas:

- `python -m pytest backend/tests -q`
- `python -m compileall backend/app backend/alembic backend/scripts`
- `npm test -- --run`
- `npm run build`
