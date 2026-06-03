# Telas Administrativas, Permissões e Logs — Plano de Design

## 1. Objetivo

Definir as telas administrativas do sistema REMOBS, mantendo compatibilidade com celular.

Embora parte da administração seja mais confortável em desktop, o sistema deve permitir ações críticas pelo celular, principalmente:

- Aprovar ou reprovar saídas;
- Consultar logs;
- Corrigir inconsistências;
- Alterar status;
- Ver usuários e permissões básicas;
- Consultar alertas.

---

## 2. Tela de aprovações pendentes

```text
┌──────────────────────────┐
│ Aprovações               │
├──────────────────────────┤
│ [Pendentes] [Aprovadas]  │
├──────────────────────────┤
│ 🟡 Saída de Anemômetro   │
│ Solicitante: João        │
│ Destino: Boia AXYS 3M    │
│ [Ver detalhes]           │
├──────────────────────────┤
│ 🟡 Silicone 200 ml       │
│ Qtd: 4 • Estoque         │
│ [Ver detalhes]           │
└──────────────────────────┘
```

### Ações

- Ver detalhes;
- Aprovar;
- Reprovar;
- Solicitar ajuste;
- Anexar observação.

### Regras

- Reprovação exige motivo;
- Aprovação de saída de componente permanente deve mostrar número de série;
- Se estoque mudou desde a solicitação, avisar;
- Todas as decisões geram log.

---

## 3. Detalhe de aprovação

```text
┌──────────────────────────┐
│ ← Aprovar saída          │
├──────────────────────────┤
│ Item                     │
│ Anemômetro Gill 5108     │
│ Série: 12345             │
├──────────────────────────┤
│ Solicitante              │
│ Maria • Operação         │
├──────────────────────────┤
│ Origem: Manutenção       │
│ Destino: Boia AXYS 3M    │
│ Motivo: troca em campo   │
├──────────────────────────┤
│ Estoque/local atual      │
│ Disponível               │
├──────────────────────────┤
│ [Reprovar] [Aprovar]     │
└──────────────────────────┘
```

### Componentes MUI

- `Card`;
- `Chip`;
- `Alert`;
- `Button`;
- `Dialog`;
- `Timeline`, se disponível, ou lista de histórico.

---

## 4. Tela de usuários

## 4.1 Lista mobile

```text
┌──────────────────────────┐
│ Usuários              +  │
├──────────────────────────┤
│ [Buscar usuário]         │
│ [Ativos] [Bloqueados]    │
├──────────────────────────┤
│ 👤 Maria                 │
│ Operação • Ativa         │
│ Último acesso: hoje      │
├──────────────────────────┤
│ 👤 Carlos                │
│ Admin • Ativo            │
└──────────────────────────┘
```

## 4.2 Detalhe do usuário

Seções:

- Dados básicos;
- Papéis;
- Permissões efetivas;
- Sessões ativas;
- Histórico de acesso;
- Ações administrativas.

### Ações

- Editar usuário;
- Alterar papel;
- Inativar;
- Bloquear/desbloquear;
- Revogar sessões;
- Redefinir senha.

### Regras

- Alteração de papel exige confirmação;
- Inativação exige motivo;
- Revogação de sessão gera log;
- Permissões efetivas devem ser visíveis para evitar confusão.

---

## 5. Tela de papéis e permissões

## 5.1 Mobile

Em celular, usar accordions:

```text
┌──────────────────────────┐
│ Papéis e permissões      │
├──────────────────────────┤
│ ▾ Operação               │
│   ✓ inventory:read       │
│   ✓ movement:request     │
│   ✓ checklist:submit     │
│   ✕ movement:approve     │
├──────────────────────────┤
│ ▸ Administrador          │
│ ▸ DGAes                  │
└──────────────────────────┘
```

## 5.2 Desktop

Em desktop, pode usar matriz/tabela.

### Regras

- Alterar permissão exige perfil autorizado;
- Alterar permissão em produção exige justificativa;
- Mostrar impacto: “X usuários afetados”;
- Gerar log com antes/depois.

---

## 6. Tela de logs de auditoria

## 6.1 Lista mobile

```text
┌──────────────────────────┐
│ Logs de auditoria     🔍 │
├──────────────────────────┤
│ [Período] [Ação] [Usuário]│
├──────────────────────────┤
│ 🟢 Saída aprovada        │
│ Admin: Carlos            │
│ Item: Gill 5108          │
│ Hoje 14:32               │
├──────────────────────────┤
│ 🔴 Acesso negado         │
│ Usuário: Maria           │
│ Ação: audit:read         │
│ Hoje 13:10               │
└──────────────────────────┘
```

## 6.2 Detalhe do log

```text
┌──────────────────────────┐
│ ← Detalhe do log         │
├──────────────────────────┤
│ Ação                     │
│ movement:approve         │
│ Status: sucesso          │
├──────────────────────────┤
│ Usuário                  │
│ Carlos • Admin           │
├──────────────────────────┤
│ Entidade                 │
│ Saída #1021              │
├──────────────────────────┤
│ Antes                    │
│ status: pending          │
│ Depois                   │
│ status: approved         │
├──────────────────────────┤
│ Justificativa            │
│ Troca programada         │
└──────────────────────────┘
```

### Filtros

- Data inicial/final;
- Usuário;
- Papel;
- Ação;
- Entidade;
- Status;
- Origem;
- Local;
- Plataforma;
- Item.

### Regras

- Logs não podem ser editados;
- Exportação aparece apenas para autorizado;
- Exportação gera log;
- Dados sensíveis devem ser mascarados quando necessário.

---

## 7. Tela de cadastros-base

Cadastros:

- Categorias de item;
- Locais;
- Tipos de plataforma;
- Tipos de sensor;
- Status;
- Campos customizados;
- Modelos de checklist;
- Unidades de medida.

### Design mobile

- Lista de cadastros;
- Detalhe em tela separada;
- Formulário simples;
- Confirmação para exclusão lógica;
- Aviso quando cadastro estiver em uso.

---

## 8. Tela de relatórios

Relatórios iniciais:

- Estoque crítico;
- Movimentações;
- Plataformas por status;
- Sensores avariados;
- Calibrações vencidas;
- Logs;
- Checklists por período.

### Mobile

- Cards de relatórios;
- Filtros básicos;
- Botão “Gerar”;
- Exportação quando autorizada;
- Aviso para relatórios muito grandes.

### Desktop

- Filtros avançados;
- Tabelas;
- Exportações;
- Gráficos.

---

## 9. Critérios de aceite

- Admin aprova saída pelo celular;
- Reprovação exige motivo;
- Tela de usuários funciona no celular;
- Permissões aparecem agrupadas por papel;
- Logs são consultáveis em cards no celular;
- Exportar relatório gera log;
- Ações administrativas aparecem somente para autorizado;
- Mudança de permissão exige confirmação.
