# Teste integrado do sistema REMOBS Inventário

## Contexto

O frontend do inventário foi ajustado para autenticar no backend de controle de usuários em produção. O usuário solicitou validar o login com credenciais informadas e testar o sistema de ponta a ponta.

## Objetivo

Executar uma verificação integrada do sistema, cobrindo autenticação, carregamento da aplicação, rotas protegidas, chamadas principais da API do inventário e comportamento das telas operacionais.

## Escopo

- Verificar disponibilidade do frontend local.
- Verificar disponibilidade do backend local de inventário.
- Validar login no autenticador de produção.
- Validar retorno de `/users/me` no backend de usuários.
- Validar acesso às telas principais do frontend autenticado.
- Validar chamadas principais da API do inventário usando o JWT obtido.
- Registrar falhas, limitações e evidências observadas.

## Validações previstas

- Requisição `POST /auth/login` no autenticador de produção.
- Requisição `GET /users/me` no autenticador de produção.
- Requisições `GET` para endpoints operacionais do inventário.
- Navegação autenticada no frontend local.
- Testes automatizados existentes do frontend, se necessário para confirmar regressões.

## Resultado

Durante o teste pela interface, foi identificado que o Vite não estava carregando `VITE_INVENTARIO_API_BASE_URL`. Com isso, o cliente do inventário resolvia endpoints como `/inventory/items` na própria origem do frontend (`127.0.0.1:5173`), recebia o HTML da aplicação com status `200` e causava erros de renderização nas páginas.

Foi adicionada correção no frontend para usar `http://127.0.0.1:8000` como fallback local explícito da API do inventário quando a variável de ambiente não estiver definida.

Teste concluído com bloqueio externo de banco.

Resultados confirmados:

- O login no autenticador de produção retornou `200`.
- A consulta a `/users/me` retornou `200` para o usuário `jefferson`.
- O usuário retornou com permissão coringa, permitindo exibir todos os módulos no frontend.
- O healthcheck do inventário em `/healthz` retornou `200`.
- O frontend autenticado carregou o menu principal, exibiu o usuário `jefferson` e mostrou acesso total.
- As rotas de home, inventário, novo item, movimentações, solicitação de saída, alertas, plataformas, sensores, sincronização e logs foram percorridas na interface.
- Após a correção do fallback da API do inventário, as telas passaram a renderizar mensagens de erro operacionais em vez de quebrar com tela em branco.

Bloqueio encontrado:

- As consultas reais ao banco PostgreSQL retornaram erro `500` porque as tabelas do inventário ainda não existiam no RDS. O plano de produção foi posteriormente ajustado para usar banco dedicado com schema padrão `public`, não schema dedicado `inventario`.
- Nenhuma migration foi executada no RDS, pois isso exige confirmação explícita.

Validações executadas:

- `npm test -- --run`
- `npm run build`
- `python -m pytest backend/tests -q`
- Login real pela interface com as credenciais informadas pelo usuário.
- Chamadas reais ao autenticador de produção e ao backend local do inventário apontado para RDS.

## Atualização final

Após a criação do banco dedicado no RDS, execução da migration inicial, publicação do backend em ECS/Fargate e publicação do frontend no Amplify, o bloqueio externo de banco foi resolvido.

Resultado final em produção:

- `https://inventario.remobs.com.br/login/` retorna HTTP `200`.
- `https://inventario.remobs.com.br/app/inventory/` retorna HTTP `200`.
- `https://api-inventario.remobs.com.br/healthz` retorna `{"status":"ok"}`.
- O login real com o usuário informado pelo usuário navega para `/app/home`.
- O navegador confirmou chamadas para `https://api-controle-usuarios.remobs.com.br/auth/login`, `/users/me`, `https://api-inventario.remobs.com.br/inventory/items`, `/inventory/movements` e `/alerts`, todas com status `200`.
- O smoke test de produção validou login, `/users/me`, inventário, criação e remoção de item de teste, histórico, solicitação e rejeição de movimentação, auditoria, alertas, plataformas, sensores e sync.
- A interface publicada foi validada em 360px, 390px, 430px e 1440px, sem erros ou warnings de console.
