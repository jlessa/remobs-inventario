# Padrões de Formulários, Listas e Interação — REMOBS

## 1. Objetivo

Definir padrões para telas de cadastro, edição, busca, listas e ações no sistema REMOBS.

Como o sistema será usado em campo pelo celular, os formulários devem ser curtos, progressivos e resistentes a perda de conexão.

---

## 2. Padrão de lista mobile

## 2.1 Estrutura

```text
Título da tela
Busca
Chips de filtro
Lista em cards
Ação principal fixa ou FAB
```

## 2.2 Card de item

Campos recomendados:

- Nome;
- Tipo;
- Marca/modelo;
- Número de série ou patrimônio, quando houver;
- Local;
- Status;
- Alerta;
- Próxima ação.

Exemplo:

```text
🟡 Silicone 200 ml
Consumível • Marca X
Estoque: 4 • Mínimo: 10
Local: Estoque
[Abrir]
```

## 2.3 Filtros rápidos

Usar chips:

- Todos;
- Crítico;
- Em manutenção;
- Avariado;
- Instalado;
- Disponível;
- Pendente;
- Sem documento.

## 2.4 Filtros avançados

Em celular, abrir em bottom sheet ou tela cheia:

- Tipo;
- Local;
- Status;
- Marca;
- Modelo;
- Plataforma;
- Período;
- Responsável.

---

## 3. Padrão de formulário mobile

## 3.1 Organização

Formulários devem ser divididos em seções:

1. Identificação;
2. Estoque/local;
3. Status/condição;
4. Documentos/fotos;
5. Revisão.

## 3.2 Campos obrigatórios

- Usar asterisco ou texto “obrigatório”;
- Mostrar erro abaixo do campo;
- Não esperar o envio final para mostrar erro simples;
- No final, listar pendências.

## 3.3 Salvamento

- Salvar rascunho automaticamente;
- Botão “Salvar rascunho” explícito;
- Mensagem “Rascunho salvo há X min”;
- Recuperar rascunho após fechar app;
- Informar se rascunho está somente no dispositivo.

## 3.4 Botões

Padrão:

- Ação primária: botão preenchido;
- Ação secundária: botão contornado;
- Ação destrutiva: botão com confirmação;
- Ações fixas no rodapé quando o formulário for longo.

---

## 4. Campos por tipo de dado

## 4.1 Texto simples

Usar `TextField`.

Exemplos:

- Nome;
- Marca;
- Modelo;
- Número de série;
- Patrimônio.

## 4.2 Texto longo

Usar `TextField multiline`.

Exemplos:

- Observação;
- Justificativa;
- Motivo de reprovação;
- Diagnóstico de manutenção.

## 4.3 Seleção

Usar `Select` para listas curtas e `Autocomplete` para listas longas.

Exemplos curtos:

- Status;
- Tipo de item;
- Condição.

Exemplos longos:

- Item de inventário;
- Plataforma;
- Sensor;
- Usuário responsável.

## 4.4 Quantidade

Para celular:

- Campo numérico com teclado numérico;
- Botões + e - quando a quantidade for pequena;
- Validação de mínimo e máximo;
- Exibir estoque disponível próximo ao campo.

## 4.5 Data

- Usar seletor de data;
- Permitir digitação quando for mais rápido;
- Validar vencimento de calibração;
- Mostrar datas críticas com alerta.

## 4.6 Fotos

Ações:

- Tirar foto;
- Escolher da galeria;
- Remover foto;
- Adicionar legenda;
- Comprimir antes de enviar.

Mostrar:

- Miniatura;
- Status de upload;
- Erro de upload;
- Pendência offline.

## 4.7 Documentos

Ações:

- Anexar PDF/imagem;
- Informar tipo de documento;
- Associar a item, sensor ou plataforma;
- Visualizar;
- Baixar, se autorizado.

---

## 5. Padrão de status

## 5.1 Chip de status

Sempre usar:

- Cor;
- Texto;
- Ícone.

Exemplo:

```text
🟢 Em operação
🟡 Inconsistência
⚪ Não instalado
🔴 Avariado
```

## 5.2 Mensagem complementar

Quando status for crítico, explicar.

Exemplo:

```text
🔴 Avariado
Sensor com defeito ou sem envio de dados.
```

---

## 6. Confirmações

Exigir confirmação para:

- Aprovar saída;
- Reprovar saída;
- Alterar estoque;
- Alterar status para avariado;
- Excluir/inativar item;
- Alterar permissões;
- Descartar rascunho;
- Resolver conflito offline.

### Padrão de diálogo

```text
Título claro
Explicação curta
Resumo da ação
Campo de motivo, se obrigatório
Cancelar
Confirmar
```

---

## 7. Erros e validações

## 7.1 Erros de campo

Exemplos:

- “Informe a quantidade.”
- “Quantidade maior que o estoque disponível.”
- “Motivo obrigatório para reprovação.”
- “Número de série já cadastrado.”

## 7.2 Erros de permissão

Exemplo:

```text
Você não tem permissão para aprovar esta solicitação.
Solicite apoio de um administrador.
```

## 7.3 Erros offline

Exemplo:

```text
Sem conexão. Salvamos esta ação no dispositivo e ela será enviada depois.
```

---

## 8. Empty states

Estados vazios devem orientar o usuário.

Exemplos:

```text
Nenhum item encontrado.
Tente remover filtros ou buscar por outro termo.
```

```text
Nenhuma solicitação pendente.
Quando a operação solicitar saída, ela aparecerá aqui.
```

```text
Você está offline.
Os dados exibidos podem estar desatualizados.
```

---

## 9. Carregamento

Usar:

- Skeleton em listas;
- Progress linear em sync;
- Spinner apenas em ações curtas;
- Mensagem clara em ações demoradas.

Evitar:

- Tela branca sem feedback;
- Spinner infinito sem explicação.

---

## 10. Critérios de aceite

- Formulário funciona em celular sem zoom;
- Campos têm label visível;
- Rascunho é salvo automaticamente;
- Erros aparecem próximos ao campo;
- Listas usam cards no celular;
- Filtros avançados não ocupam toda a tela sem necessidade;
- Foto mostra status de upload;
- Ação crítica exige confirmação;
- Usuário sempre entende se está online ou offline.
