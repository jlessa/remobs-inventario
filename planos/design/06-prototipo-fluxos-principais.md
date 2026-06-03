# Protótipo Textual dos Fluxos Principais — REMOBS

## 1. Objetivo

Descrever os fluxos principais do sistema em formato textual, servindo como base para prototipação no Figma ou implementação direta com Material UI.

---

# 2. Fluxo: login e entrada no app

## Ator

Todos os usuários.

## Passos

1. Usuário abre o sistema no celular;
2. Tela de login aparece;
3. Usuário informa e-mail e senha;
4. Sistema valida credenciais;
5. Sistema carrega permissões;
6. Sistema exibe tela inicial personalizada;
7. Sistema registra login no log de acesso.

## Exceções

- Senha incorreta;
- Usuário inativo;
- Usuário bloqueado;
- Sem conexão;
- Sessão expirada.

## Tela final

- Operação vê ações rápidas de campo;
- Admin vê aprovações pendentes;
- DGAes vê dashboard e alertas;
- Desenvolvedor vê atalhos de configuração quando autorizado.

---

# 3. Fluxo: solicitação de saída de item

## Ator

Operação.

## Passos

1. Usuário acessa **Operação**;
2. Toca em **Solicitar saída**;
3. Busca item por nome, série, patrimônio ou leitura de código;
4. Seleciona quantidade;
5. Informa origem;
6. Informa destino;
7. Informa motivo;
8. Anexa foto, se necessário;
9. Envia solicitação;
10. Sistema registra solicitação pendente;
11. Sistema registra log;
12. Admin recebe alerta.

## Exceções

- Estoque insuficiente;
- Item indisponível;
- Usuário sem permissão;
- Sem conexão.

## Offline

Se estiver offline:

1. Sistema salva solicitação localmente;
2. Marca como “pendente de sincronização”;
3. Exibe contador de pendências;
4. Sincroniza quando a conexão voltar;
5. Se houver conflito de estoque, solicita revisão.

---

# 4. Fluxo: aprovação de saída

## Ator

Administrador.

## Passos

1. Admin acessa **Alertas** ou **Aprovações**;
2. Abre solicitação pendente;
3. Confere item, quantidade, solicitante, destino e motivo;
4. Sistema mostra estoque atual;
5. Admin aprova ou reprova;
6. Se reprovar, informa motivo;
7. Sistema atualiza status;
8. Sistema ajusta estoque/local quando aplicável;
9. Sistema registra log;
10. Operação recebe notificação.

## Exceções

- Estoque mudou desde a solicitação;
- Item foi inativado;
- Admin tenta aprovar solicitação própria;
- Sessão expirou;
- Permissão removida.

---

# 5. Fluxo: cadastro de consumível

## Ator

Admin, Desenvolvedor ou Compras com permissão.

## Passos

1. Usuário acessa **Inventário**;
2. Toca em **Novo item**;
3. Seleciona **Consumível**;
4. Preenche item, marca, modelo e unidade;
5. Define local e quantidade;
6. Define estoque ideal e mínimos;
7. Anexa foto ou nota fiscal;
8. Revisa dados;
9. Salva;
10. Sistema gera log.

## Validações

- Nome obrigatório;
- Local obrigatório;
- Quantidade não negativa;
- Estoque mínimo não pode ser maior que estoque ideal sem confirmação;
- Alertar possível duplicidade por nome/marca/modelo.

---

# 6. Fluxo: cadastro de componente permanente

## Ator

Admin, Desenvolvedor ou Manutenção com permissão.

## Passos

1. Usuário acessa **Inventário**;
2. Toca em **Novo item**;
3. Seleciona **Componente permanente**;
4. Informa tipo, item, marca e modelo;
5. Informa número de série ou patrimônio;
6. Define condição e local;
7. Anexa foto/documento;
8. Salva;
9. Sistema cria histórico inicial;
10. Sistema registra log.

## Validações

- Número de série duplicado deve ser bloqueado ou confirmado por Admin;
- Local obrigatório;
- Condição obrigatória;
- Se local for “Boia”, plataforma deve ser informada;
- Se condição for “Avariado”, motivo obrigatório.

---

# 7. Fluxo: alteração de status de plataforma

## Ator

Admin, Manutenção ou Operação solicitando alteração.

## Passos

1. Usuário abre detalhe da plataforma;
2. Toca em **Alterar status**;
3. Escolhe novo status;
4. Informa motivo, se status for crítico;
5. Anexa evidência, se necessário;
6. Sistema valida permissão;
7. Sistema salva alteração ou cria solicitação;
8. Sistema registra log;
9. Alertas são atualizados.

## Status

- Em operação;
- Em montagem;
- Disponível para montagem;
- Em manutenção/offline.

## Regras

- Verde deve indicar operação regular;
- Vermelho exige motivo;
- Histórico deve mostrar status anterior e novo;
- Alteração feita offline deve aguardar sincronização.

---

# 8. Fluxo: vínculo de sensor à plataforma

## Ator

Admin ou Manutenção.

## Passos

1. Usuário abre detalhe da plataforma;
2. Acessa seção **Sensores**;
3. Toca em **Adicionar sensor**;
4. Busca sensor por tipo/modelo/série;
5. Confirma instalação;
6. Informa data, posição ou observação;
7. Sistema altera local/status do sensor;
8. Sistema registra histórico;
9. Sistema gera log.

## Exceções

- Sensor já instalado em outra plataforma;
- Sensor avariado;
- Sensor sem calibração válida;
- Usuário sem permissão.

---

# 9. Fluxo: registro de inconsistência de sensor

## Ator

Operação, Manutenção ou Admin.

## Passos

1. Usuário abre detalhe do sensor;
2. Toca em **Registrar inconsistência**;
3. Seleciona tipo de inconsistência;
4. Descreve o problema;
5. Anexa foto/documento/log, se houver;
6. Sistema altera status para amarelo;
7. Sistema cria alerta;
8. Sistema registra log.

## Tipos de inconsistência

- Medição fora do padrão;
- Dados ausentes;
- Documentação faltando;
- Calibração vencida;
- Problema físico observado;
- Outro.

---

# 10. Fluxo: checklist em campo

## Ator

Operação.

## Passos

1. Usuário acessa **Operação**;
2. Toca em **Novo checklist**;
3. Seleciona plataforma;
4. Escolhe modelo de checklist;
5. Preenche etapas;
6. Anexa fotos;
7. Revisa resumo;
8. Envia;
9. Sistema registra log;
10. Checklist fica disponível no histórico.

## Offline

- Salvar rascunho local;
- Permitir fotos locais;
- Marcar como pendente;
- Sincronizar depois;
- Resolver conflitos, se plataforma/status tiver mudado.

---

# 11. Fluxo: resolução de conflito offline

## Ator

Usuário que criou a ação e Admin, quando necessário.

## Causa comum

Um item foi alterado no servidor antes da ação offline ser sincronizada.

## Tela sugerida

```text
Conflito encontrado

Sua versão:
Quantidade solicitada: 4
Estoque visto: 10

Versão atual:
Estoque atual: 2

[Ajustar solicitação]
[Descartar]
[Enviar para Admin]
```

## Regras

- Nunca sobrescrever automaticamente;
- Mostrar diferenças;
- Registrar decisão em log;
- Preservar payload original;
- Permitir reenvio após ajuste.

---

# 12. Fluxo: consulta de log

## Ator

Admin ou perfil autorizado.

## Passos

1. Usuário acessa **Menu > Logs**;
2. Aplica filtros;
3. Abre card de log;
4. Consulta antes/depois;
5. Exporta, se autorizado;
6. Exportação gera novo log.

---

# 13. Critérios globais de aceite dos fluxos

- Fluxos funcionam em celular;
- Usuário recebe feedback após cada ação;
- Ações críticas exigem confirmação;
- Permissões são respeitadas no frontend e backend;
- Logs são gerados para cada ação crítica;
- Offline não causa perda de dados;
- Conflitos são tratados de forma explícita;
- O usuário sempre entende o próximo passo.
