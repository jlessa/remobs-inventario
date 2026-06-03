# Logs, Auditoria e Observabilidade — Plano de Implementação

## 1. Objetivo

Garantir rastreabilidade completa das ações do sistema REMOBS.

O sistema deve permitir responder perguntas como:

- Quem alterou este item?
- Quando o estoque foi alterado?
- Qual era o valor antes e depois?
- Quem aprovou a saída?
- Qual sensor foi removido de uma boia?
- Qual usuário tentou acessar uma função sem permissão?
- Quais ações foram feitas offline e sincronizadas depois?

---

## 2. Tipos de logs

## 2.1 Log de auditoria

Registro de ações de negócio.

Exemplos:

- Criação de item;
- Edição de item;
- Exclusão lógica;
- Alteração de estoque;
- Solicitação de saída;
- Aprovação ou reprovação;
- Alteração de status operacional;
- Vínculo ou desvínculo de sensor;
- Upload de foto ou documento;
- Correção de inconsistência;
- Alteração de permissões;
- Alteração de usuário;
- Sincronização de ação offline.

## 2.2 Log de acesso

Registro de autenticação e sessão.

Exemplos:

- Login bem-sucedido;
- Login falho;
- Logout;
- Sessão expirada;
- Sessão revogada;
- Recuperação de senha;
- Acesso negado por falta de permissão.

## 2.3 Log técnico

Registro para diagnóstico.

Exemplos:

- Erros da API;
- Tempo de resposta elevado;
- Falha no envio de e-mail;
- Falha de upload;
- Falha de sincronização offline;
- Erro em job assíncrono;
- Erro de integração externa.

## 2.4 Log de sincronização offline

Registro específico para uso em campo.

Exemplos:

- Ação criada offline;
- Ação enviada para fila;
- Ação sincronizada com sucesso;
- Conflito detectado;
- Conflito resolvido;
- Ação descartada por permissão expirada.

---

## 3. Modelo de log de auditoria

Tabela sugerida: `audit_logs`

| Campo | Tipo | Descrição |
|---|---|---|
| id | UUID | Identificador do log |
| occurred_at | timestamp | Data/hora do evento |
| actor_user_id | UUID | Usuário responsável |
| actor_name_snapshot | texto | Nome do usuário no momento |
| actor_role_snapshot | texto | Papel do usuário no momento |
| action | texto | Ação realizada |
| entity_type | texto | Tipo da entidade afetada |
| entity_id | UUID | ID da entidade afetada |
| entity_label_snapshot | texto | Nome/código exibível da entidade |
| before_data | JSON | Dados antes da alteração |
| after_data | JSON | Dados depois da alteração |
| diff | JSON | Diferenças principais |
| reason | texto | Justificativa informada pelo usuário |
| source | texto | web, mobile, offline_sync, job, api |
| ip_address | texto | IP de origem, quando disponível |
| user_agent | texto | Navegador/dispositivo |
| device_id | texto | Identificador do dispositivo, quando aplicável |
| correlation_id | texto | ID para rastrear a requisição |
| status | texto | success, failed, denied |
| metadata | JSON | Dados adicionais |

---

## 4. Regras de auditoria

## 4.1 Append-only

Logs de auditoria não devem ser editados nem apagados pelo sistema comum.

Se houver necessidade legal ou administrativa de remoção, ela deve ser feita por processo controlado, com registro próprio.

## 4.2 Diferença antes/depois

Sempre que houver alteração de cadastro ou estoque, salvar:

- Valor anterior;
- Novo valor;
- Usuário;
- Data/hora;
- Motivo;
- Origem da alteração.

## 4.3 Exclusão lógica

Preferir exclusão lógica em entidades de negócio.

Campos sugeridos:

- `deleted_at`
- `deleted_by`
- `delete_reason`

## 4.4 Justificativa obrigatória

Exigir justificativa para:

- Correção manual de estoque;
- Reprovação de saída;
- Cancelamento de movimentação;
- Alteração de status para avariado ou manutenção;
- Desvincular sensor de plataforma;
- Alterar permissões de usuário.

---

## 5. Eventos que devem gerar log

## 5.1 Autenticação

- Login sucesso;
- Login falha;
- Logout;
- Recuperação de senha;
- Troca de senha;
- Usuário bloqueado;
- Usuário desbloqueado;
- Sessão expirada;
- Sessão revogada.

## 5.2 Usuários e permissões

- Criação de usuário;
- Edição de usuário;
- Inativação de usuário;
- Mudança de papel;
- Adição de permissão;
- Remoção de permissão;
- Tentativa de acesso negado.

## 5.3 Inventário

- Criação de consumível;
- Edição de consumível;
- Alteração de quantidade;
- Criação de componente permanente;
- Edição de componente permanente;
- Alteração de local;
- Alteração de condição;
- Upload de foto;
- Upload de nota fiscal;
- Vincular item a patrimônio;
- Desvincular item de patrimônio.

## 5.4 Plataformas, cascos e sensores

- Criação de plataforma;
- Alteração de status;
- Vincular casco;
- Desvincular casco;
- Vincular sensor;
- Desvincular sensor;
- Marcar sensor como avariado;
- Marcar sensor como inconsistente;
- Registrar manutenção;
- Registrar calibração;
- Anexar documentação.

## 5.5 Movimentações e aprovações

- Solicitar saída;
- Aprovar saída;
- Reprovar saída;
- Cancelar solicitação;
- Confirmar retirada;
- Confirmar devolução;
- Transferir local;
- Atualizar estoque por inventário físico.

## 5.6 Offline

- Criar rascunho offline;
- Enfileirar ação;
- Sincronizar ação;
- Detectar conflito;
- Resolver conflito;
- Rejeitar ação por permissão insuficiente;
- Rejeitar ação por item alterado no servidor.

---

## 6. Consulta de logs no sistema

## 6.1 Tela de logs

Filtros mínimos:

- Período;
- Usuário;
- Papel;
- Tipo de entidade;
- Ação;
- Status;
- Local;
- Plataforma;
- Item;
- Origem: online, offline, job, API.

## 6.2 Exibição mobile

Em celular, não usar tabela larga.

Usar cards com:

- Ícone da ação;
- Título curto;
- Usuário;
- Data/hora;
- Entidade;
- Status;
- Botão **Ver detalhes**.

## 6.3 Detalhe do log

Mostrar:

- Quem fez;
- Quando fez;
- O que fez;
- Dados antes;
- Dados depois;
- Diferença destacada;
- Justificativa;
- Origem;
- ID da requisição;
- Status.

---

## 7. Observabilidade técnica

Além dos logs de negócio, a aplicação deve possuir observabilidade técnica.

## 7.1 Métricas recomendadas

- Tempo médio de resposta da API;
- Quantidade de erros 4xx e 5xx;
- Número de logins falhos;
- Número de sincronizações offline pendentes;
- Tamanho da fila de e-mails;
- Uploads com falha;
- Alertas emitidos por dia;
- Movimentações pendentes de aprovação.

## 7.2 Alertas técnicos

Emitir alerta para responsáveis técnicos quando:

- API estiver fora do ar;
- Erros 5xx aumentarem;
- Fila de jobs travar;
- Backup falhar;
- Banco chegar perto do limite de armazenamento;
- Uploads falharem repetidamente.

---

## 8. Privacidade e dados sensíveis

Cuidados:

- Não registrar senha, token ou segredo em log;
- Evitar registrar dados pessoais desnecessários;
- Mascarar e-mail ou telefone quando exportar logs, se exigido;
- Controlar quem pode consultar logs;
- Registrar acesso à tela de logs;
- Definir política de retenção.

---

## 9. Retenção e exportação

## 9.1 Retenção

Definir com a equipe REMOBS:

- Logs de auditoria: retenção longa;
- Logs técnicos: retenção menor;
- Logs de acesso: retenção intermediária;
- Backups: política própria.

## 9.2 Exportação

Permitir exportação por usuários autorizados:

- CSV;
- XLSX, se necessário;
- PDF de relatório, se necessário;
- JSON para auditoria técnica.

Toda exportação deve gerar log.

---

## 10. Critérios de aceite

- Toda alteração de estoque gera log com antes/depois;
- Toda aprovação ou reprovação gera log;
- Toda falha de permissão gera log;
- Admin consegue filtrar logs por item, usuário e período;
- O log mostra origem online ou offline;
- Dados sensíveis não aparecem em logs técnicos;
- Logs não podem ser alterados pela interface comum;
- Exportação de logs gera novo log.
