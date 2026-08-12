# Correção do upload de arquivos e imagens

## Contexto

Os botões **Anexar foto** e **Anexar documento** na tela de detalhe do item existiam apenas como UI estática. O banco já tinha as tabelas `files` e `entity_files`, mas não havia API, serviço de armazenamento nem integração no frontend.

## Objetivo

Implementar o fluxo completo de upload, listagem, download e remoção lógica de fotos e documentos vinculados a itens de inventário.

## Escopo

### Backend

- Configuração de armazenamento local (`REMOBS_STORAGE_LOCAL_PATH`, limite de tamanho).
- Serviço de storage em disco.
- Endpoints:
  - `GET /inventory/items/{id}/files`
  - `POST /inventory/items/{id}/files` (multipart)
  - `GET /inventory/items/{id}/files/{file_id}/content`
  - `DELETE /inventory/items/{id}/files/{file_id}`
- Auditoria de upload e exclusão.
- Validação de MIME, tamanho e papel do arquivo (`foto` / `documento`).

### Frontend

- Ligar botões de anexar a input de arquivo.
- Listar anexos no detalhe do item.
- Pré-visualizar imagens e baixar documentos com autenticação.
- Remover anexo com confirmação.

### Fora de escopo nesta entrega

- Bucket S3/MinIO em produção (preparado para evolução via storage key).
- Upload real de fotos no checklist de campo (hoje continua como checklist boolean).
- Anexos em plataformas/sensores.

## Validações

- Testes de contrato no backend para upload/list/download/delete.
- Teste frontend do detalhe com botões e listagem.
- `CHANGELOG.md` atualizado.

## Resultado

Implementado.

- Backend: storage local + endpoints de listagem, upload multipart, download e soft delete com auditoria.
- Frontend: botões de anexar funcionais no detalhe do item, grade de anexos, preview de imagem e remoção.
- Testes:
  - backend `test_item_file_upload_list_download_and_delete` e `test_item_file_rejects_invalid_image_type` (2 passed; pytest pode permanecer aberto no Windows por engine async);
  - frontend `inventory-detail-files.test.tsx` (2 passed).
- Observação: storage dual `local`|`s3`. Bucket de produção criado: `inventario-remobs` (ver `planos/2026-08-06-bucket-s3-inventario-remobs.md`). Produção efetiva no ECS ainda depende de deploy da imagem com `boto3` + envs S3 + task role.
