# Cadastro de plataformas e sensores pelo frontend

## Contexto

O usuário informou que deve ser possível cadastrar plataformas e sensores pelo frontend, mas o botão de cadastro não aparece na interface.

## Objetivo

Identificar a causa raiz da ausência dos botões de cadastro e ajustar o frontend para permitir o acesso ao fluxo de criação de plataformas e sensores, mantendo consistência com a arquitetura e os padrões já adotados no projeto.

## Escopo

- Investigar as páginas de plataformas e sensores no frontend.
- Verificar rotas, permissões, componentes de ação e serviços relacionados.
- Implementar testes focados no comportamento esperado.
- Corrigir a interface e, se necessário, os fluxos de criação.
- Atualizar o changelog do projeto.

## Etapas

1. Ler as instruções obrigatórias do repositório e dos projetos relacionados.
2. Reproduzir o problema por inspeção de testes, rotas e componentes.
3. Comparar o padrão usado em cadastro de inventário com plataformas e sensores.
4. Criar ou ajustar teste automatizado que comprove a presença das ações de cadastro.
5. Implementar a correção no frontend.
6. Executar validações automatizadas disponíveis.
7. Registrar a alteração no `CHANGELOG.md`.

## Validações previstas

- Executar os testes do frontend relacionados a navegação e serviços.
- Executar build ou verificação equivalente do frontend.
- Validar visualmente, quando possível, que os botões aparecem nas páginas de plataformas e sensores.

## Resultado

Concluído. A causa raiz foi a ausência de implementação no frontend: as páginas de plataformas e sensores não tinham botões de cadastro, rotas de criação, formulários ou métodos de serviço para chamar os endpoints já existentes no backend.

Foram adicionados:

- Botão "Nova plataforma" para usuários com permissão `platform:update`.
- Botão "Novo sensor" para usuários com permissão `sensor:update`.
- Rotas `/app/platforms/new` e `/app/sensors/new`.
- Formulários de cadastro de plataformas e sensores.
- Métodos `createPlatform` e `createSensor` no cliente de inventário.
- Testes automatizados para validar botões de cadastro e chamadas aos endpoints.

Validações executadas:

- `npm test -- --run` no frontend: 5 arquivos e 14 testes aprovados.
- `npm run build` no frontend: build concluído com sucesso.
- Abertura do app local no navegador interno: a aplicação carregou e redirecionou rota protegida para login, como esperado sem sessão autenticada.
