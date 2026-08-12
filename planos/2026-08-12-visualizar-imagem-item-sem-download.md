# Visualizar imagem do item sem forçar download

## Contexto

No detalhe do item, anexos de imagem exibiam miniatura, mas a única ação era **Baixar**, forçando download via `anchor.download`.

## Objetivo

Permitir abrir e visualizar a imagem na própria tela (Dialog), sem download para fotos. Documentos continuam com download.

## Escopo

- Frontend: `InventoryDetailPage`
- Testes: `inventory-detail-files.test.tsx`
- Changelog e este plano

## Etapas

1. Adicionar Dialog/lightbox com a object URL já carregada em `previews`
2. Clique na miniatura e botão Visualizar abrem o Dialog
3. Remover botão Baixar para MIME `image/*`
4. Manter Baixar para documentos
5. Cobrir com testes

## Validação

- Foto: Visualizar abre modal; sem botão Baixar
- Documento: botão Baixar permanece e inicia download

## Resultado

Implementado e commitado em `fix: visualizar imagem do item sem forçar download`.
