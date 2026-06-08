# Arquitetura de Telas e Navegação — REMOBS

## 1. Objetivo

Definir o mapa de telas do sistema REMOBS com navegação mobile-first.

O usuário em campo deve conseguir acessar rapidamente:

- Inventário;
- Solicitação de saída;
- Plataformas;
- Sensores;
- Checklists;
- Alertas;
- Sincronização.

---

## 2. Navegação principal mobile

```text
Bottom Navigation
├── Início
├── Inventário
├── Operação
├── Alertas
└── Menu
```

### 2.1 Início

Resumo operacional:

- Plataformas em operação;
- Plataformas em manutenção;
- Sensores avariados;
- Estoque crítico;
- Solicitações pendentes;
- Pendências offline.

### 2.2 Inventário

Consulta e gestão de:

- Consumíveis;
- Componentes permanentes;
- Estoques;
- Locais;
- Movimentações;
- Fotos e documentos.

### 2.3 Operação

Fluxos de campo:

- Solicitar saída;
- Preencher checklist;
- Registrar foto;
- Registrar manutenção;
- Confirmar retirada;
- Confirmar devolução;
- Escanear item, se houver QR Code/código.

### 2.4 Alertas

- Estoque mínimo;
- Sensor avariado;
- Plataforma offline;
- Calibração vencida;
- Solicitação aguardando aprovação;
- Pendência de sincronização.

### 2.5 Menu

Acesso a módulos secundários:

- Plataformas;
- Sensores;
- Checklists;
- Sincronização;
- Sair.

Itens devem aparecer conforme permissão.

---

## 3. Mapa de rotas

## 3.1 Rotas públicas

```text
/login
```

## 3.2 Rotas autenticadas

```text
/app/home
/app/inventory
/app/inventory/new
/app/inventory/:id
/app/inventory/:id/edit
/app/inventory/:id/history
/app/movements
/app/movements/new
/app/movements/:id
/app/platforms
/app/platforms/:id
/app/sensors
/app/sensors/:id
/app/checklists
/app/checklists/new
/app/checklists/:id
/app/alerts
/app/sync
/app/menu
```

## 3.3 Rotas fora do escopo

Este sistema não possui telas administrativas nem rotas públicas de recuperação de senha. Usuários, papéis, permissões e recuperação de senha ficam sob responsabilidade dos projetos próprios do ecossistema REMOBS.

---

## 4. Estrutura padrão de tela mobile

```text
┌────────────────────────────┐
│ AppBar                     │
│ Título + conexão + perfil  │
├────────────────────────────┤
│ Busca/filtros/contexto     │
├────────────────────────────┤
│ Conteúdo em cards/listas   │
│                            │
│                            │
├────────────────────────────┤
│ Ação fixa, quando houver   │
├────────────────────────────┤
│ Bottom Navigation          │
└────────────────────────────┘
```

---

## 5. Hierarquia das telas

## 5.1 Inventário

```text
Inventário
├── Lista de itens
│   ├── Busca
│   ├── Filtros
│   ├── Ordenação
│   └── Cards de item
├── Detalhe do item
│   ├── Resumo
│   ├── Estoque/local
│   ├── Documentos
│   ├── Fotos
│   ├── Histórico
│   └── Ações
├── Novo item
├── Editar item
└── Histórico do item
```

## 5.2 Movimentações

```text
Movimentações
├── Lista de solicitações
├── Nova solicitação de saída
├── Detalhe da solicitação
├── Aprovar/Reprovar
├── Confirmar retirada
└── Confirmar devolução
```

## 5.3 Plataformas

```text
Plataformas
├── Lista de plataformas
├── Detalhe da plataforma
│   ├── Resumo
│   ├── Status
│   ├── Casco
│   ├── Sistemas
│   ├── Sensores
│   ├── Documentos
│   ├── Histórico
│   └── Ações
└── Editar status
```

## 5.4 Sensores

```text
Sensores
├── Lista de sensores
├── Detalhe do sensor
│   ├── Resumo
│   ├── Status
│   ├── Plataforma vinculada
│   ├── Calibração
│   ├── Documentos
│   ├── Histórico
│   └── Ações
└── Editar status
```

## 5.5 Checklists

```text
Checklists
├── Modelos disponíveis
├── Novo checklist
├── Checklist em rascunho
├── Checklist enviado
└── Histórico de checklists
```

---

## 6. Navegação por permissão

A navegação deve ser montada dinamicamente.

Exemplos:

- Usuário de Operação não vê tela de gestão de usuários;
- Usuário DGAes vê dashboards e alertas, mas não vê edição de estoque;
- Admin vê aprovações pendentes;
- Desenvolvedor vê cadastros-base;
- Compras vê estoque crítico e notas fiscais.

---

## 7. Padrões por tamanho de tela

## 7.1 Celular

- Bottom navigation;
- Filtros em bottom sheet;
- Cards;
- Dialogs em tela cheia;
- Ações fixas no rodapé;
- Apenas informações essenciais na lista.

## 7.2 Tablet

- Bottom navigation ou navigation rail;
- Cards em duas colunas;
- Filtros laterais opcionais;
- Detalhe com abas.

## 7.3 Desktop

- Drawer fixo;
- Tabelas completas;
- Filtros visíveis;
- Visualização mestre-detalhe;
- Exportações e relatórios com mais espaço.

---

## 8. Busca e filtros globais

## 8.1 Busca

Busca deve aceitar:

- Nome do item;
- Marca;
- Modelo;
- Número de série;
- Patrimônio;
- Plataforma;
- Sensor;
- Local.

## 8.2 Filtros frequentes

- Tipo;
- Status;
- Local;
- Estoque crítico;
- Avariado;
- Em manutenção;
- Pendente de aprovação;
- Com documentação faltando.

---

## 9. Estados vazios

Cada tela deve ter estado vazio útil.

Exemplos:

- “Nenhum item encontrado.”
- “Nenhuma solicitação pendente.”
- “Você ainda não possui checklists em rascunho.”
- “Sem conexão. Os dados exibidos podem estar desatualizados.”

---

## 10. Critérios de aceite

- Bottom navigation funciona no celular;
- Menu mostra apenas módulos permitidos;
- Usuário acessa inventário em até dois toques após login;
- Fluxo de solicitar saída é acessível pela aba Operação;
- Alertas críticos aparecem na tela inicial;
- O menu não exibe telas administrativas;
- Desktop não compromete o design mobile-first.
