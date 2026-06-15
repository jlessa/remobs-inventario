# Plano de execução - Análise das planilhas em `docs`

## Contexto

O diretório `docs/` contém duas planilhas recebidas como referência para o sistema de inventário REMOBS. A tarefa é ler os arquivos, identificar quais informações podem virar funcionalidades ou cadastros no sistema e apontar quais dados ainda estão incompletos ou precisam de validação.

## Objetivo

Analisar a estrutura e o conteúdo das planilhas para propor incrementos ao sistema de inventário, respeitando as regras do projeto, a arquitetura existente e a integração com os projetos relacionados do ecossistema REMOBS.

## Escopo

- Ler as instruções operacionais deste repositório.
- Ler a configuração local do ecossistema.
- Validar a existência das instruções dos projetos relacionados.
- Extrair abas, colunas, amostras e padrões relevantes das duas planilhas em `docs/`.
- Mapear possíveis funcionalidades, entidades, campos e fluxos derivados das planilhas.
- Listar lacunas de informação que impedem implementação direta ou exigem decisão de negócio.

## Fora do escopo

- Implementar código no frontend ou backend.
- Executar migrações de banco de dados.
- Criar commit.
- Alterar as planilhas originais.

## Etapas

1. Validar instruções e arquivos obrigatórios do repositório.
2. Criar este plano de execução.
3. Extrair metadados e conteúdo relevante das planilhas.
4. Comparar os dados identificados com os domínios já previstos para o sistema.
5. Consolidar recomendações de funcionalidades e lacunas de informação.
6. Atualizar o changelog com o registro da análise documental.

## Validações

- Confirmar que as duas planilhas foram localizadas em `docs/`.
- Confirmar que a leitura foi feita sem alterar os arquivos originais.
- Confirmar que a documentação produzida está em português do Brasil.
- Confirmar que nenhum commit foi criado sem autorização explícita.

## Resultado

Foram analisadas as duas planilhas localizadas em `docs/`:

- `INVENTARIO.xlsx`
- `Ficha_Campo_MEq_AX39_DD_MM_AA.xlsx`

A análise identificou oportunidades de evolução para o sistema nos seguintes domínios:

- Importação assistida de inventário de laboratório, paiol e consumíveis.
- Separação entre itens patrimoniais, itens consumíveis e ferramentas.
- Cadastro estruturado de estações operacionais, projetos, clientes, contratos, responsáveis e avisos de campo.
- Gestão de pendências operacionais por estação, com prioridade, prazo, responsável, executor, itens necessários e conclusão.
- Modelos detalhados de checklist de campo por tipo de manobra, com evidências fotográficas, condições ambientais, tripulação, mergulho, sensores, problemas, ações pós-campo e observações.
- Catálogos auxiliares de falhas, motivos e itens afetados para padronizar diagnósticos de campo.

Também foram encontradas lacunas de informação que exigem saneamento antes de uma importação definitiva:

- O inventário do paiol não possui quantidades nem data de última atualização preenchidas.
- O inventário de laboratório tem baixa cobertura para condição, data de teste, saída, destino, solicitante e última atualização.
- Há valores textuais e não padronizados em campos que deveriam ser numéricos ou enumerados, como quantidade e condição.
- Há duplicidades de número de série ou TAG no inventário de laboratório que precisam ser validadas.
- A aba de consumíveis de teste possui apenas três registros e contém célula residual fora da tabela esperada.
- O cadastro de estações possui lacunas em latitude, longitude, backup, contatos, avisos e tábua de marés.
- A coluna calculada de responsável da estação nas pendências retorna erro quando lida como valor calculado.
- A lista de clientes tem contatos estruturados parcialmente e usa campos duplicados de nome, e-mail e telefone.

Nenhum código foi implementado, nenhuma migração foi executada e nenhum commit foi criado.
