# Plano de execução - Implementação do checklist de campo detalhado

## Contexto

A análise das planilhas em `docs/` identificou que as fichas de campo possuem um checklist operacional mais completo do que o formulário atual do sistema. O usuário confirmou a implementação do item 4 da análise: checklist de campo detalhado. O cadastro estruturado de estações não faz parte desta tarefa.

## Objetivo

Evoluir o formulário e a visualização de checklists para registrar dados operacionais de campo inspirados nas fichas analisadas, usando a persistência JSON já existente em `answers` e `evidence`, sem criar novas tabelas nem migrações de banco.

## Escopo

- Ampliar o formulário de checklist no frontend com seções de operação, condições ambientais, equipe, fotos obrigatórias, inspeção técnica, problemas e pós-campo.
- Manter compatibilidade com o endpoint atual de checklists.
- Enviar as respostas detalhadas no campo `answers`.
- Exibir as respostas em grupos legíveis na tela de detalhe.
- Criar teste automatizado para validar a presença dos novos campos e o envio do payload detalhado.
- Atualizar o changelog.

## Fora do escopo

- Criar cadastro estruturado de estações.
- Criar entidades de cliente, contrato ou manutenção programada.
- Importar dados das planilhas para o banco.
- Executar migrações.
- Criar commit.

## Estratégia técnica

O backend já armazena `answers` e `evidence` como JSON. A implementação ficará concentrada no frontend, preservando o contrato atual. O formulário montará um payload com chaves agrupadas, como `operacao.tipo_manobra`, `ambiente.chuva`, `equipe.embarcacao_1`, `fotografias.adcp` e `pos_campo.entrega_ficha`.

## Etapas

1. Criar um teste de frontend que falhe enquanto o checklist detalhado não existir.
2. Implementar o formulário detalhado em `ChecklistFormPage`.
3. Agrupar as respostas na tela de detalhe em `ChecklistDetailPage`.
4. Ajustar tipos auxiliares somente se necessário.
5. Atualizar `CHANGELOG.md`.
6. Executar os testes de frontend relacionados.

## Validações

- O teste novo deve falhar antes da implementação.
- O teste novo deve passar após a implementação.
- O build de frontend deve ser executado, se os testes passarem.
- Nenhuma alteração deve ser feita nas planilhas originais.
- Nenhum commit deve ser criado sem confirmação explícita.

## Resultado

Implementação concluída no frontend, preservando o contrato atual do backend por meio dos campos JSON `answers` e `evidence`.

Foram adicionadas seções detalhadas ao formulário de checklist de campo, incluindo dados da operação, condições ambientais, equipe, embarcações, fotografias obrigatórias, inspeção técnica, problemas, solução e pós-campo. A tela de detalhe passou a agrupar as respostas por seção e a exibir valores booleanos como `Sim` ou `Não`.

Validações executadas:

- `npm test -- checklist-field-form.test.tsx --run`: passou após o ciclo vermelho-verde.
- `npm test -- --run`: passou com 6 arquivos de teste e 15 testes.
- `npm run build`: passou com geração do build de produção do frontend.
- Navegação local em navegador real para `/app/checklists/new`: redirecionamento esperado para `/login` sem token autenticado, sem erros de console.
