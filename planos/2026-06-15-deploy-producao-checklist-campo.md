# Plano de execução - Deploy em produção do checklist de campo

## Contexto

O usuário autorizou o push dos commits locais e o deploy em produção pelo AWS Amplify usando o profile AWS `aws-remobs`.

## Objetivo

Publicar em produção o frontend atualizado com cadastro de plataformas e sensores, checklist de campo detalhado e documentação associada.

## Escopo

- Fazer push da branch atual para o repositório remoto.
- Publicar o artefato `frontend/dist` no app AWS Amplify de produção.
- Validar o status do job do Amplify.
- Validar as rotas públicas relevantes após a publicação.

## Fora do escopo

- Alterar backend, ECS, banco de dados, DNS ou migrações.
- Criar novos recursos AWS.
- Expor credenciais ou URLs temporárias de upload do Amplify.

## Etapas

1. Validar estado do Git e fazer push da branch.
2. Confirmar profile AWS, conta, região, ambiente e comandos planejados.
3. Executar deploy manual no Amplify.
4. Corrigir falhas encontradas na validação de produção.
5. Reexecutar testes, build e deploy quando necessário.
6. Validar o domínio público.

## Validações

- `npm test -- --run`
- `npm run build`
- Job do Amplify com status `SUCCEED`
- Rotas públicas do frontend com HTTP `200`
- API de inventário com HTTP `200` em `/healthz`

## Resultado

Em andamento. Será atualizado após a validação final do deploy.
