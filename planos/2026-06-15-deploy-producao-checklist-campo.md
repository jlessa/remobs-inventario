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
