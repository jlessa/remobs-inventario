# Plano de execução - Carga das planilhas em produção

## Contexto

O usuário informou que o dashboard de produção continua exibindo poucos registros porque os dados das planilhas ainda não foram carregados no banco de produção.

## Objetivo

Inserir em produção os dados possíveis das planilhas existentes em `docs/`, respeitando os modelos já disponíveis no sistema e sem inventar campos que não existam no backend.

## Escopo

- Ler `docs/INVENTARIO.xlsx` e `docs/Ficha_Campo_MEq_AX39_DD_MM_AA.xlsx`.
- Preparar uma carga idempotente para evitar duplicação em novas execuções.
- Inserir itens de inventário, categorias, locais e saldos.
- Inserir sensores identificados a partir das linhas do tipo `Sensor`.
- Inserir plataformas a partir da aba `Cadastro Estacoes`.
- Inserir checklists a partir das abas `FichaCampo*` não marcadas como teste.
- Validar as contagens no banco e no dashboard após a carga.
- Registrar o resultado no changelog.

## Fora do escopo

- Criar novas tabelas ou alterar o schema de produção.
- Importar dados para funcionalidades que ainda não possuem modelo persistido específico, como pendências operacionais separadas.
- Apagar ou sobrescrever dados existentes em produção.
- Executar comandos AWS sem confirmação explícita do usuário.

## Etapas

1. Mapear as abas e os campos disponíveis nas planilhas.
2. Gerar payload normalizado da carga.
3. Preparar script idempotente de importação para execução dentro da task do backend.
4. Solicitar confirmação dos comandos AWS planejados.
5. Executar a carga em produção.
6. Validar contagens no banco e no frontend publicado.
7. Atualizar o changelog com os dados efetivamente carregados.

## Resultado

Concluído.

A carga foi executada em produção por uma task avulsa do ECS, usando o mesmo task definition do backend (`remobs-inventario-backend:3`) e um pacote temporário hospedado em S3 por URL pré-assinada. O bucket temporário `remobs-inventario-import-220790920077-20260615` e o objeto `imports/import_bundle.zip` foram removidos após a execução.

O caminho por `ecs execute-command` foi tentado primeiro, mas a task ativa do serviço não tinha `executeCommandEnabled` e a task temporária com ECS Exec retornou `TargetNotConnected`, por ausência de configuração adequada de Session Manager/task role. Para não alterar IAM nem reiniciar o serviço, foi adotada a execução por task avulsa com download de pacote temporário.

Validações executadas antes da carga:

- Geração local do payload a partir das planilhas.
- Compilação dos scripts Python.
- Ensaio local em banco SQLite temporário, incluindo reexecução idempotente.
- Diagnóstico read-only em produção confirmando conexão ao banco e contagens iniciais.

Dados inseridos em produção:

- 728 itens de inventário importados das planilhas.
- 113 plataformas importadas da aba `Cadastro Estacoes`.
- 218 sensores importados a partir das linhas do tipo `Sensor`.
- 12 checklists importados das abas `FichaCampo*` não marcadas como teste.
- 7 checklists ficaram com status `submitted`.

Validação final no banco de produção, com a mesma regra usada pelo dashboard:

- Itens cadastrados: 729.
- Estoque crítico: 0.
- Plataformas em operação: 90.
- Plataformas em manutenção: 13.
- Sensores com alerta: 18.
- Checklists registrados: 12.
- Checklists enviados: 7.

Observação: o total de itens cadastrados é 729 porque já havia 1 item ativo antes da carga e foram importados 728 novos itens.
