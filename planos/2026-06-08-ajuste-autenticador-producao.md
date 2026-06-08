# Ajuste do autenticador de produção no frontend

## Contexto

O formulário de login do frontend estava enviando a requisição para a própria origem do Vite, resultando em `POST http://127.0.0.1:5173/auth/login` com retorno `404 Not Found`.

Esse comportamento ocorre quando a URL base do autenticador fica vazia ou configurada como `/`, pois o Axios passa a resolver `/auth/login` contra a origem atual da aplicação.

## Objetivo

Garantir que o cliente de autenticação do frontend aponte para `https://api-controle-usuarios.remobs.com.br` por padrão, fazendo com que o login use `https://api-controle-usuarios.remobs.com.br/auth/login`.

## Escopo

- Adicionar teste de regressão para a URL padrão do autenticador.
- Criar configuração centralizada para URLs base das APIs.
- Atualizar o cliente Axios de autenticação para usar a URL de produção quando não houver sobrescrita explícita por ambiente.
- Atualizar o ambiente de produção do frontend.
- Registrar a correção no changelog.

## Validações previstas

- `npm test -- --run`
- `npm run build`

## Resultado

Concluído.

Foi criada uma configuração centralizada de URLs das APIs no frontend. O cliente de autenticação agora usa `https://api-controle-usuarios.remobs.com.br` quando `VITE_AUTH_API_BASE_URL` não estiver definido ou estiver vazio após normalização. O arquivo `.env.production` também foi ajustado para apontar explicitamente para o autenticador de produção.

Com isso, a chamada de login passa a resolver para `https://api-controle-usuarios.remobs.com.br/auth/login`, e não mais para a origem local do Vite.

Também foi adicionado teste direto do cliente Axios para garantir que `/auth/login` resolva para a URL completa do autenticador de produção.

Validações executadas:

- `npm test -- --run`
- `npm run build`
