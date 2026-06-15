# Deploy em produção do cadastro de plataformas e sensores

## Contexto

O usuário solicitou publicar em produção a correção que adiciona o cadastro de plataformas e sensores pelo frontend, usando o perfil AWS `aws-remobs` pela CLI.

## Objetivo

Publicar o frontend atualizado no AWS Amplify de produção do REMOBS Inventário, sem criar commit, mantendo o backend existente e validando o acesso público após o deploy.

## Escopo

- Validar o artefato local do frontend antes da publicação.
- Identificar o app e a branch de produção do AWS Amplify.
- Publicar o artefato manualmente pela AWS CLI com o perfil informado.
- Validar o domínio público de produção.
- Registrar o resultado da publicação.

## Fora de escopo

- Criar commit ou push para repositório remoto.
- Alterar backend, banco de dados, migrações ou recursos ECS.
- Executar migrações de produção.

## Etapas

1. Confirmar configuração de deploy já documentada no projeto.
2. Validar credenciais e região do perfil AWS informado.
3. Reexecutar testes e build do frontend.
4. Criar pacote de deploy do frontend.
5. Enviar o pacote ao Amplify e iniciar o deployment.
6. Acompanhar o status do job até conclusão ou falha.
7. Validar o domínio público do frontend.
8. Atualizar o changelog e este plano com o resultado.

## Validações previstas

- `npm test -- --run` no frontend.
- `npm run build` no frontend.
- Consulta do job do Amplify até status final.
- Requisição HTTP para o domínio público do inventário.

## Resultado

Concluído.

- Perfil AWS usado: `aws-remobs`.
- App Amplify: `remobs-inventario-frontend`.
- Branch publicada: `prod`.
- Job do Amplify: `12`.
- Status final do job: `SUCCEED`.
- Artefato publicado: frontend gerado por `npm run build`, com bundle `assets/index-B_umn9DO.js`.

Validações executadas:

- `npm test -- --run`: 5 arquivos e 14 testes aprovados.
- `npm run build`: build concluído com sucesso.
- `https://inventario.remobs.com.br/login/`: HTTP 200.
- `https://inventario.remobs.com.br/app/platforms/`: HTTP 200.
- `https://inventario.remobs.com.br/app/sensors/`: HTTP 200.
- `https://api-inventario.remobs.com.br/healthz`: HTTP 200.
- O HTML publicado referencia `assets/index-B_umn9DO.js`.
- O bundle publicado contém os textos "Nova plataforma" e "Novo sensor".
