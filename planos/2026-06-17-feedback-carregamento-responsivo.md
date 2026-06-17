# Feedback visual de carregamento responsivo

## Contexto

As telas que buscam dados não exibiam nenhum indicador enquanto a requisição estava em andamento. Como consequência, o usuário via momentaneamente os estados vazios (por exemplo, "Nenhum item encontrado") antes dos dados chegarem, o que dava a impressão de tela quebrada, especialmente em conexões mais lentas.

## Objetivo

Adicionar feedback visual de carregamento em todas as telas, garantindo que o conteúdo seja totalmente responsivo em telas pequenas.

## Escopo

- Novo componente `frontend/src/components/LoadingState.tsx`: spinner centralizado com mensagem, largura fluida, espaçamento e altura mínima responsivos por ponto de quebra (`xs`/`sm`) e `role="status"` para acessibilidade.
- Estado de carregamento (`loading`) nas telas que buscam dados, encerrado em `finally`, com exibição do `LoadingState` durante a busca:
  - Listas: inventário, plataformas, sensores, operação, alertas e checklists.
  - Dashboard, sincronização e solicitação de saída (carga dos itens).
  - Telas de detalhe de item, plataforma, sensor e checklist, substituindo o texto "Carregando..." por `LoadingState`.
- Correção dos estados vazios para só aparecerem quando o carregamento termina (`!loading`).
- Indicador de progresso nos botões de envio dos formulários de item, sensor, plataforma e checklist, desabilitando o botão durante a gravação para evitar envios duplicados.

## Validações

- Verificação de tipos com `tsc -b` sem erros.
- Suíte de testes do frontend: 18 testes aprovados.
- Build de produção (`npm run build`) concluído com sucesso.
- Layout responsivo preservado: o componente não usa larguras fixas e mantém o padrão mobile-first do Material UI.

## Resultado

Todas as telas passam a exibir um indicador de carregamento claro e responsivo enquanto os dados são buscados, e os estados vazios deixam de piscar durante o carregamento.

## Publicação

- Frontend publicado no AWS Amplify de produção, branch `prod`, com o profile AWS `aws-remobs`, região `sa-east-1`.
