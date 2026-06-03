# Roadmap, Sprints e Critérios de Aceite — Sistema REMOBS

## 1. Estratégia

O sistema deve ser construído por entregas incrementais, sempre mantendo uma versão testável.

Prioridade recomendada:

1. Segurança e permissões;
2. Inventário base;
3. Fluxo de saída e aprovação;
4. Plataformas e sensores;
5. Operação mobile em campo;
6. Offline/sincronização;
7. Alertas e relatórios;
8. Integrações.

---

## 2. Fase 0 — Descoberta e validação

## Objetivo

Transformar o levantamento inicial em escopo validado.

## Atividades

- Revisar categorias de inventário;
- Validar papéis de usuários;
- Confirmar fluxos de aprovação;
- Definir quais dados são obrigatórios;
- Mapear documentos existentes;
- Levantar dispositivos usados em campo;
- Confirmar requisitos offline;
- Definir indicadores do dashboard.

## Entregáveis

- Backlog inicial;
- Mapa de entidades;
- Protótipo de baixa fidelidade;
- Matriz de permissões validada;
- Lista de campos obrigatórios.

## Critérios de aceite

- Equipe concorda com os módulos da primeira versão;
- Papéis e permissões iniciais estão definidos;
- Telas principais estão desenhadas em mobile-first;
- Fluxos críticos têm responsáveis claros.

---

## 3. Sprint 1 — Base técnica, login e layout

## Objetivo

Criar a fundação do sistema.

## Funcionalidades

- Estrutura frontend React + TypeScript + Material UI;
- Estrutura backend;
- Banco de dados inicial;
- Tela de login;
- Autenticação;
- Sessão;
- Layout mobile-first;
- Menu inferior para celular;
- Menu lateral para telas maiores;
- Perfil do usuário;
- Logout;
- Logs de login.

## Critérios de aceite

- Usuário consegue logar e sair;
- Usuário inativo não consegue logar;
- Login falho gera log;
- Layout funciona em celular;
- Navegação principal está pronta;
- Backend valida autenticação.

---

## 4. Sprint 2 — Usuários, papéis e permissões

## Objetivo

Implementar controle de acesso.

## Funcionalidades

- Cadastro de usuário;
- Edição de usuário;
- Inativação;
- Papéis;
- Permissões;
- Middleware de autorização no backend;
- Ocultação de ações não permitidas no frontend;
- Tela de gestão de usuários;
- Log de alteração de permissão.

## Critérios de aceite

- Operação não acessa tela de logs;
- Operação não aprova saída;
- Admin consegue aprovar saída quando módulo existir;
- Tentativa sem permissão retorna erro;
- Alteração de papel gera log.

---

## 5. Sprint 3 — Inventário de consumíveis

## Objetivo

Permitir cadastro e consulta de consumíveis.

## Funcionalidades

- Cadastro de item consumível;
- Lista com busca e filtros;
- Detalhe do item;
- Estoque por local;
- Estoque ideal e mínimo;
- Upload de foto;
- Nota fiscal;
- Histórico inicial;
- Alertas simples de estoque baixo.

## Critérios de aceite

- Usuário autorizado cadastra consumível;
- Operação visualiza pelo celular;
- Estoque abaixo do mínimo aparece como alerta;
- Alteração de quantidade gera log;
- Lista funciona sem tabela larga no celular.

---

## 6. Sprint 4 — Componentes permanentes

## Objetivo

Controlar equipamentos rastreáveis.

## Funcionalidades

- Cadastro de componente permanente;
- Número de série;
- Número patrimonial/TERP/CADEM;
- Condição;
- Local;
- Fotos;
- Documentos;
- Histórico de localização;
- Filtro por status e local.

## Critérios de aceite

- Componente permanente possui histórico;
- Alteração de local gera movimentação;
- Item avariado gera alerta;
- Foto aparece no detalhe;
- Documento pode ser anexado.

---

## 7. Sprint 5 — Movimentações e aprovações

## Objetivo

Implementar solicitação de saída e aprovação.

## Funcionalidades

- Solicitar saída pelo celular;
- Ver estoque disponível;
- Anexar justificativa;
- Aprovar/reprovar por Admin;
- Confirmar retirada;
- Confirmar devolução;
- Histórico da movimentação;
- Notificações por e-mail ou painel;
- Logs completos.

## Critérios de aceite

- Operação solicita saída;
- Admin aprova;
- Estoque é atualizado corretamente;
- Reprovação exige motivo;
- Todas as etapas aparecem no histórico.

---

## 8. Sprint 6 — Plataformas, cascos e sistemas

## Objetivo

Cadastrar plataformas e sua estrutura operacional.

## Funcionalidades

- Cadastro de plataformas fixas;
- Cadastro de plataformas móveis;
- Cadastro de cascos;
- Sistemas: energia, processamento, aquisição, transmissão, sinalização, fundeio, estruturas;
- Status por cor;
- Vincular componentes a sistemas;
- Histórico de status.

## Critérios de aceite

- Plataforma exibe status por cor;
- Casco pode ser vinculado à plataforma;
- Sistema interno pode ter componentes;
- Alteração de status exige justificativa quando crítico;
- Histórico pode ser consultado.

---

## 9. Sprint 7 — Sensores e documentação técnica

## Objetivo

Controlar sensores oceanográficos e meteorológicos.

## Funcionalidades

- Cadastro de sensor;
- Tipo e família;
- Modelo e série;
- Status operacional;
- Calibração;
- Documentos;
- Vínculo com plataforma;
- Histórico de instalação e remoção.

## Critérios de aceite

- Sensor pode ser vinculado a uma plataforma;
- Sensor avariado gera alerta;
- Calibração vencida gera alerta;
- Documento de calibração pode ser anexado;
- Histórico de instalação é exibido.

---

## 10. Sprint 8 — Checklists de campo

## Objetivo

Permitir registro operacional por celular.

## Funcionalidades

- Templates de checklist;
- Checklist por plataforma;
- Perguntas obrigatórias;
- Respostas sim/não, texto, número, foto e seleção;
- Rascunho automático;
- Envio;
- Histórico.

## Critérios de aceite

- Operação preenche checklist pelo celular;
- Checklist salva rascunho;
- Pergunta obrigatória bloqueia envio se vazia;
- Fotos são anexadas;
- Envio gera log.

---

## 11. Sprint 9 — Offline e sincronização

## Objetivo

Dar suporte a campo com conexão instável.

## Funcionalidades

- Indicador online/offline;
- Cache de dados principais;
- Fila offline;
- Sincronização manual e automática;
- Tela de pendências;
- Tratamento de conflitos;
- Logs de sync.

## Critérios de aceite

- Usuário consegue salvar rascunho offline;
- Ação offline sincroniza ao voltar conexão;
- Conflito é exibido e não sobrescreve dados silenciosamente;
- Usuário vê quantas ações estão pendentes;
- Sincronização gera log.

---

## 12. Sprint 10 — Dashboards, relatórios e alertas

## Objetivo

Gerar visão de gestão.

## Funcionalidades

- Dashboard inicial;
- Plataformas por status;
- Estoque crítico;
- Sensores avariados;
- Calibrações vencidas;
- Solicitações pendentes;
- Relatórios filtráveis;
- Exportação.

## Critérios de aceite

- Dashboard abre no celular;
- Cards mostram indicadores críticos;
- Usuário acessa detalhe do indicador;
- Relatórios respeitam permissões;
- Exportação gera log.

---

## 13. Sprint 11 — Integrações e endurecimento

## Objetivo

Preparar produção e futuras integrações.

## Funcionalidades

- Integração com e-mail;
- Integração patrimonial futura;
- Integração com compras futura;
- Backup automatizado;
- Monitoramento;
- Testes de carga;
- Testes de segurança;
- Ajustes finais de UX.

## Critérios de aceite

- Backup está configurado;
- Erros técnicos são monitorados;
- E-mails de alerta funcionam;
- Sistema possui documentação de deploy;
- Fluxos principais foram testados em celular real.

---

## 14. Plano de testes

## 14.1 Testes funcionais

- Login;
- Permissões;
- Cadastro de item;
- Movimentação;
- Aprovação;
- Status de plataforma;
- Vínculo de sensor;
- Checklist;
- Alertas;
- Logs.

## 14.2 Testes mobile

Testar em:

- Largura 360px;
- Largura 390px;
- Largura 430px;
- Android Chrome;
- iOS Safari, se aplicável;
- Rede instável;
- Modo offline;
- Uso com brilho alto/ambiente externo.

## 14.3 Testes de segurança

- Senha fraca;
- Login inválido;
- Token expirado;
- Acesso sem permissão;
- Upload inválido;
- Injeção em filtros;
- Tentativa de alteração de dados por API sem permissão.

---

## 15. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Conexão ruim em campo | PWA offline, rascunhos e fila de sync |
| Permissões mal definidas | Matriz validada e logs de acesso negado |
| Dados duplicados de inventário | Campos de diferenciação, busca e validação |
| Tabelas ruins no celular | Cards, filtros e telas de detalhe |
| Falta de rastreabilidade | Logs append-only desde a primeira sprint |
| Fotos muito pesadas | Compressão antes do upload |
| Conflito offline | Tela de resolução e versionamento |
| Adoção baixa | Teste com usuários de campo desde o protótipo |

---

## 16. Marco de versão 1.0

A versão 1.0 deve conter:

- Login;
- Permissões;
- Usuários;
- Inventário de consumíveis;
- Componentes permanentes;
- Saída/aprovação;
- Plataformas;
- Sensores;
- Checklists;
- Logs;
- Alertas básicos;
- Dashboard inicial;
- Uso mobile-first funcional.
