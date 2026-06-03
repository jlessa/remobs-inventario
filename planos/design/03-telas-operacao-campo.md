# Telas de Operação em Campo — Plano de Design Mobile

## 1. Objetivo

Desenhar as telas usadas por equipes em campo pelo celular.

Prioridades:

- Rapidez;
- Poucos toques;
- Legibilidade;
- Salvar rascunhos;
- Suporte offline;
- Fotos e evidências;
- Evitar preenchimento repetitivo.

---

## 2. Tela de login mobile

```text
┌──────────────────────────┐
│ REMOBS                   │
│ Inventário e Operação    │
│                          │
│ [ E-mail              ]  │
│ [ Senha               ]  │
│                          │
│ [ Entrar              ]  │
│                          │
│ Esqueci minha senha      │
│                          │
│ Online                   │
└──────────────────────────┘
```

### Componentes MUI

- `Container`;
- `Paper` ou `Card`;
- `TextField`;
- `Button`;
- `Alert`;
- `Typography`.

### Regras

- Mostrar erro direto;
- Não limpar o e-mail após erro de senha;
- Exibir bloqueio temporário quando ocorrer;
- Avisar se não houver conexão;
- Não permitir primeiro login offline.

---

## 3. Tela inicial do operador

```text
┌──────────────────────────┐
│ Início        Online  👤 │
├──────────────────────────┤
│ Pendências offline: 0    │
├──────────────────────────┤
│ [Solicitar saída]        │
│ [Novo checklist]         │
├──────────────────────────┤
│ Alertas críticos         │
│ 🔴 2 sensores avariados  │
│ 🟡 3 estoques baixos     │
├──────────────────────────┤
│ Plataformas              │
│ 🟢 Boia AXYS 3M          │
│ 🔴 Boia AXYS 2.4         │
├──────────────────────────┤
│ Início Inventário Oper...│
└──────────────────────────┘
```

### Conteúdo

- Ações rápidas;
- Alertas críticos;
- Plataformas recentes;
- Checklists em rascunho;
- Status de sincronização.

### Componentes MUI

- `AppBar`;
- `Card`;
- `Button`;
- `Chip`;
- `List`;
- `BottomNavigation`;
- `Badge`.

---

## 4. Lista de inventário mobile

```text
┌──────────────────────────┐
│ Inventário        🔍  ⚙ │
├──────────────────────────┤
│ [Buscar item/série...]   │
│ [Todos] [Crítico] [Local]│
├──────────────────────────┤
│ 🟡 Silicone 200 ml       │
│ Marca X • Estoque: 4     │
│ Local: Estoque           │
│ Abaixo do mínimo         │
├──────────────────────────┤
│ 🟢 Anemômetro Gill       │
│ Série: 5108              │
│ Local: Manutenção        │
├──────────────────────────┤
│ + Novo item              │
└──────────────────────────┘
```

### Regras

- Busca sempre no topo;
- Filtros rápidos por chips;
- Cards em vez de tabela;
- Cada card mostra status, nome, tipo, local e alerta;
- Ação principal pode ser FAB para usuário autorizado.

### Componentes MUI

- `TextField` com ícone de busca;
- `Chip`;
- `Card`;
- `Stack`;
- `Fab`;
- `Skeleton` para carregamento.

---

## 5. Detalhe do item

```text
┌──────────────────────────┐
│ ← Anemômetro Gill     ⋮  │
├──────────────────────────┤
│ 🟢 Operacional           │
│ Marca: Gill              │
│ Modelo: WindSonic 5108   │
│ Série: 12345             │
├──────────────────────────┤
│ Local atual              │
│ Manutenção               │
├──────────────────────────┤
│ Ações                    │
│ [Solicitar saída]        │
│ [Anexar foto]            │
├──────────────────────────┤
│ Documentos               │
│ Histórico                │
└──────────────────────────┘
```

### Abas ou seções

- Resumo;
- Estoque/local;
- Documentos;
- Fotos;
- Histórico;
- Logs, se autorizado.

### Regras

- Mostrar número de série com destaque;
- Copiar código ao toque;
- Ações devem respeitar permissão;
- Histórico deve abrir em lista mobile;
- Foto deve poder ser tirada pela câmera.

---

## 6. Solicitar saída

```text
┌──────────────────────────┐
│ ← Solicitar saída        │
├──────────────────────────┤
│ Item                     │
│ [Buscar ou escanear]     │
│                          │
│ Quantidade               │
│ [-] 1 [+]                │
│                          │
│ Origem                   │
│ [Estoque]                │
│ Destino                  │
│ [Boia / Manutenção / ...]│
│                          │
│ Motivo                   │
│ [Texto obrigatório]      │
│                          │
│ [Salvar rascunho]        │
│ [Enviar solicitação]     │
└──────────────────────────┘
```

### Regras

- Motivo obrigatório;
- Validar estoque disponível;
- Permitir anexar foto;
- Permitir rascunho offline;
- Se offline, enviar para fila;
- Mostrar confirmação após envio.

### Componentes MUI

- `Autocomplete`;
- `TextField`;
- `ButtonGroup` para quantidade;
- `Select`;
- `Dialog` de confirmação;
- `Snackbar`.

---

## 7. Checklist de campo

```text
┌──────────────────────────┐
│ ← Checklist AXYS         │
│ Rascunho salvo há 1 min  │
├──────────────────────────┤
│ 1/8 Energia              │
│ Baterias instaladas?     │
│ ( ) Sim  ( ) Não         │
│                          │
│ Quantidade               │
│ [ 4 ]                    │
│                          │
│ Foto                     │
│ [Tirar foto]             │
├──────────────────────────┤
│ [Voltar]        [Próximo]│
└──────────────────────────┘
```

### Regras

- Dividir por etapas;
- Indicar progresso;
- Salvar automaticamente;
- Permitir foto;
- Bloquear envio se obrigatório estiver faltando;
- Mostrar resumo antes do envio;
- Suportar offline.

### Componentes MUI

- `Stepper` ou progresso simples;
- `RadioGroup`;
- `TextField`;
- `Button`;
- `LinearProgress`;
- `Card`.

---

## 8. Detalhe da plataforma

```text
┌──────────────────────────┐
│ ← Boia AXYS 3M           │
├──────────────────────────┤
│ 🟢 Em operação           │
│ Última transmissão: 10:42│
├──────────────────────────┤
│ Casco                    │
│ AX-23                    │
├──────────────────────────┤
│ Sistemas                 │
│ Energia        🟢        │
│ Transmissão    🟢        │
│ Sensores       🟡        │
├──────────────────────────┤
│ Sensores                 │
│ Gill 5108      🟢        │
│ PTB110         🟡        │
└──────────────────────────┘
```

### Regras

- Status sempre no topo;
- Sistemas agrupados;
- Sensores com status;
- Ação de editar status apenas para autorizado;
- Checklist relacionado visível.

---

## 9. Detalhe do sensor

```text
┌──────────────────────────┐
│ ← PTB110                 │
├──────────────────────────┤
│ 🟡 Inconsistência        │
│ Barômetro                │
│ Série: 99881             │
├──────────────────────────┤
│ Instalado em             │
│ Boia AXYS 3M             │
├──────────────────────────┤
│ Calibração               │
│ Vence em 20 dias         │
├──────────────────────────┤
│ [Registrar inconsistência]│
│ [Anexar documento]       │
└──────────────────────────┘
```

---

## 10. Tela de sincronização

```text
┌──────────────────────────┐
│ Sincronização            │
├──────────────────────────┤
│ Status: Offline          │
│ Última sync: ontem 16:20 │
├──────────────────────────┤
│ Pendências               │
│ 🟡 Checklist AXYS        │
│ 🟡 Foto Anemômetro       │
│ 🟡 Saída Silicone        │
├──────────────────────────┤
│ [Tentar sincronizar]     │
└──────────────────────────┘
```

### Regras

- Mostrar pendências;
- Permitir tentar novamente;
- Mostrar erro detalhado;
- Não perder dados;
- Exibir conflitos de forma clara.

---

## 11. Critérios de aceite

- Operador consegue solicitar saída em menos de 1 minuto;
- Checklist pode ser preenchido com uma mão;
- Fotos podem ser anexadas pelo celular;
- Rascunho não é perdido ao fechar o navegador;
- Sistema mostra claramente quando está offline;
- Cards são legíveis em tela pequena;
- Ações sem permissão não aparecem ou aparecem bloqueadas com explicação.
