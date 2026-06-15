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

Concluído.

- Branch publicada no GitHub: `codex/implementacao-inicial-remobs-inventario`.
- Profile AWS usado: `aws-remobs`.
- Conta AWS validada: `220790920077`.
- Região: `sa-east-1`.
- App Amplify: `d1oidnxd2f4saq`.
- Branch Amplify: `prod`.
- Job final do Amplify: `18`.
- Status final do job: `SUCCEED`.

Durante a validação, foi identificado que as rotas diretas novas retornavam `404` porque o script de fallbacks do SPA não incluía `/app/platforms/new/`, `/app/sensors/new/`, `/app/checklists/` e `/app/checklists/new/`. A lista de fallbacks foi corrigida, coberta por teste automatizado e republicada.

Também foi identificado que o empacotamento inicial com `Compress-Archive` gerava entradas internas com separador de caminho do Windows, impedindo o Amplify de publicar corretamente os arquivos em subdiretórios. O pacote final foi gerado com entradas POSIX, como `login/index.html` e `app/checklists/new/index.html`.

Validações executadas:

- `npm test -- spa-fallbacks.test.ts --run`: 1 teste aprovado.
- `npm test -- --run`: 7 arquivos de teste e 16 testes aprovados.
- `npm run build`: build concluído com sucesso.
- Job `18` do Amplify: etapas `DEPLOY` e `VERIFY` concluídas com `SUCCEED`.
- `https://inventario.remobs.com.br/`: HTTP `200`.
- `https://inventario.remobs.com.br/login/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/platforms/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/platforms/new/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/sensors/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/sensors/new/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/checklists/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/checklists/new/`: HTTP `200`.
- `https://api-inventario.remobs.com.br/healthz`: HTTP `200`.
- O bundle publicado `assets/index-ZTJ89eMu.js` contém os textos `Nova plataforma`, `Novo sensor`, `Ficha de Campo V2` e `Novo checklist de campo`.

## Ajuste posterior de cache

Após o deploy, o usuário informou que não encontrava as alterações no ambiente de produção. A verificação confirmou que o HTML e o bundle publicados continham as alterações, mas o PWA ainda usava o cache `remobs-inventario-v1` no service worker, o que poderia manter respostas antigas no navegador do usuário.

Foi implementada a troca para `remobs-inventario-v2`, com `self.skipWaiting()` na instalação e `self.clients.claim()` na ativação, para acelerar a substituição do service worker e remover caches antigos.

Validações adicionais executadas:

- `npm test -- service-worker-cache.test.ts --run`: 1 teste aprovado.
- `npm test -- --run`: 8 arquivos de teste e 17 testes aprovados.
- `npm run build`: build concluído com sucesso e `frontend/dist/sw.js` gerado com `remobs-inventario-v2`.
- Job `19` do Amplify: etapas `DEPLOY` e `VERIFY` concluídas com `SUCCEED`.
- `https://inventario.remobs.com.br/login/`: HTTP `200` após republicação.
- `https://inventario.remobs.com.br/app/platforms/new/`: HTTP `200` após republicação.
- `https://inventario.remobs.com.br/app/sensors/new/`: HTTP `200` após republicação.
- `https://inventario.remobs.com.br/app/checklists/new/`: HTTP `200` após republicação.
- `https://inventario.remobs.com.br/sw.js`: publicado com `remobs-inventario-v2`, `skipWaiting` e `clients.claim`.
