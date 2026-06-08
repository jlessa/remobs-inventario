# Design System Mobile-First com Material UI — REMOBS

## 1. Objetivo

Definir as diretrizes visuais e de interação para o sistema REMOBS, priorizando uso em celular durante operações de campo.

O design deve ser:

- Simples;
- Rápido;
- Legível sob luz externa;
- Operável com uma mão;
- Resiliente em baixa conectividade;
- Acessível;
- Consistente com Material UI.

---

## 2. Princípios mobile-first

## 2.1 Projetar primeiro para celular

A menor tela deve guiar a experiência.

Priorizar larguras:

- 360px;
- 390px;
- 430px.

Depois adaptar para:

- Tablet;
- Notebook;
- Desktop.

## 2.2 Evitar tabelas largas

Em celular:

- Usar cards;
- Usar listas compactas;
- Usar accordions;
- Usar chips de status;
- Usar telas de detalhe;
- Usar filtros em bottom sheet.

Em desktop:

- Tabelas podem ser usadas;
- Colunas extras podem aparecer;
- Filtros laterais podem ser exibidos.

## 2.3 Ações principais sempre acessíveis

Em campo, o usuário deve conseguir agir rápido.

Padrões recomendados:

- Botão flutuante para ação principal;
- Barra inferior fixa para ações de fluxo;
- Botões grandes;
- Confirmação clara para ações críticas;
- Feedback imediato por snackbar/toast.

## 2.4 Salvar automaticamente

Formulários longos devem:

- Salvar rascunho local;
- Mostrar último salvamento;
- Continuar de onde parou;
- Avisar pendências obrigatórias;
- Funcionarem offline quando possível.

---

## 3. Componentes Material UI recomendados

## 3.1 Estrutura

- `CssBaseline`;
- `ThemeProvider`;
- `AppBar`;
- `Toolbar`;
- `BottomNavigation`;
- `Drawer` responsivo;
- `Container`;
- `Stack`;
- `Box`;
- `Grid` responsivo.

## 3.2 Conteúdo

- `Card`;
- `CardContent`;
- `Typography`;
- `Chip`;
- `Avatar`;
- `List`;
- `ListItem`;
- `Accordion`;
- `Divider`;
- `Tabs` quando houver poucas abas.

## 3.3 Formulários

- `TextField`;
- `Select`;
- `Autocomplete`;
- `Checkbox`;
- `RadioGroup`;
- `Switch`;
- `DatePicker`, se disponível no projeto;
- `Button`;
- `IconButton`;
- `FormHelperText`.

## 3.4 Feedback

- `Snackbar`;
- `Alert`;
- `Dialog`;
- `LinearProgress`;
- `CircularProgress`;
- `Skeleton`;
- `Badge`.

## 3.5 Navegação e filtros

- `BottomNavigation` no celular;
- `Drawer` no desktop;
- `Breadcrumbs` apenas em telas maiores;
- `Chip` para filtros rápidos;
- `SwipeableDrawer` ou `Dialog fullScreen` para filtros no celular.

---

## 4. Tema visual

## 4.1 Cores de status

Usar cores com significado fixo:

| Status | Cor | Uso |
|---|---|---|
| Verde | Operacional | Em operação, ok, aprovado |
| Amarelo | Atenção | Em montagem, inconsistência, pendente |
| Cinza | Neutro | Não instalado, disponível, rascunho |
| Vermelho | Crítico | Avariado, offline, manutenção crítica, erro |

Importante: não depender apenas da cor. Sempre exibir texto e ícone.

## 4.2 Tipografia

Recomendações:

- Tamanho mínimo de texto em formulário: 16px;
- Títulos claros e curtos;
- Labels sempre visíveis;
- Evitar textos longos em botões;
- Preferir linguagem direta.

## 4.3 Espaçamento e toque

- Alvos de toque com pelo menos 48px de altura;
- Espaço adequado entre botões;
- Botões críticos longe de ações comuns;
- Barra inferior com área segura para celulares modernos;
- Evitar elementos pequenos no canto da tela.

---

## 5. Layout responsivo

## 5.1 Celular

Padrão:

```text
┌──────────────────────────┐
│ AppBar: título + status  │
├──────────────────────────┤
│ Busca / filtro rápido    │
├──────────────────────────┤
│ Cards/listas             │
│                          │
│                          │
├──────────────────────────┤
│ Bottom navigation        │
└──────────────────────────┘
```

## 5.2 Tablet

- Cards em duas colunas;
- Filtros laterais opcionais;
- Mais informações por linha;
- Drawer temporário ou fixo.

## 5.3 Desktop

- Drawer fixo;
- Tabelas com colunas completas;
- Painéis lado a lado.

---

## 6. Navegação recomendada no celular

Barra inferior com 4 ou 5 itens no máximo:

1. **Início**
2. **Inventário**
3. **Operação**
4. **Alertas**
5. **Menu**

Dentro de **Menu**:

- Plataformas;
- Sensores;
- Checklists;
- Documentos;
- Sincronização;
- Sair.

---

## 7. Padrões de status

## 7.1 Plataformas/cascos

- Verde: Em operação;
- Amarelo: Em montagem;
- Cinza: Disponível para montagem;
- Vermelho: Em manutenção/offline.

## 7.2 Sensores

- Verde: Em operação;
- Amarelo: Inconsistência;
- Cinza: Não instalado;
- Vermelho: Avariado.

## 7.3 Movimentações

- Cinza: Rascunho;
- Amarelo: Pendente;
- Verde: Aprovada/concluída;
- Vermelho: Reprovada/cancelada.

---

## 8. Acessibilidade

O sistema deve ser usado em condições difíceis, por isso acessibilidade também melhora a operação em campo.

Regras:

- Texto legível;
- Contraste adequado;
- Botões grandes;
- Ícones com texto;
- Estados visuais claros;
- Feedback para erro e sucesso;
- Navegação por teclado em desktop;
- Labels em campos de formulário;
- Não usar somente placeholder como rótulo;
- Mensagens de erro próximas ao campo.

---

## 9. Estados de conexão

A interface deve mostrar claramente:

- Online;
- Offline;
- Sincronizando;
- Pendências para enviar;
- Erro de sincronização;
- Última sincronização.

Exemplo:

```text
Offline • 3 ações pendentes
```

ou

```text
Sincronizado há 2 min
```

---

## 10. Microcopy recomendada

Usar mensagens objetivas.

Exemplos:

- “Salvo como rascunho.”
- “Sem conexão. A ação será sincronizada depois.”
- “Saída solicitada. Aguardando aprovação.”
- “Estoque insuficiente para esta saída.”
- “Você não tem permissão para aprovar esta solicitação.”
- “Foto anexada.”
- “Conflito encontrado. Revise antes de enviar.”

---

## 11. Checklist de aceite do design system

- Telas funcionam em 360px de largura;
- Bottom navigation não passa de 5 itens;
- Ações principais têm botão claro;
- Não há tabela larga no celular;
- Cards mostram status textual e visual;
- Formulários têm labels e validação;
- Tela offline existe;
- AppBar mostra contexto e conexão;
- Usuário consegue executar fluxo principal com uma mão;
- Layout desktop aproveita espaço extra sem quebrar o mobile.
