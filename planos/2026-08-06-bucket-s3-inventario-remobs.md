# Bucket S3 para arquivos e imagens do inventário

## Contexto

O upload de fotos e documentos passou a funcionar via API, mas o storage inicial era disco local. Em ECS Fargate isso é efêmero. Foi solicitado bucket dedicado para persistir anexos.

## Decisão

- Nome do bucket: `inventario-remobs` (correção ortográfica de “iventario-remobs”)
- Profile AWS: `aws-remobs`
- Conta: `220790920077`
- Região: `sa-east-1`
- Prefixo de objetos: `remobs-inventario/`
- Backend: `REMOBS_STORAGE_BACKEND=s3`

## Execução

1. Implementar backend dual (`local` | `s3`) em `file_storage.py`.
2. Adicionar dependência `boto3`.
3. Criar bucket privado com:
   - block public access
   - criptografia SSE-S3
   - versionamento
   - tags de projeto
   - política deny sem TLS
4. Criar role IAM `remobs-inventario-backend-task-role` com policy inline `remobs-inventario-s3-files`.
5. Script `backend/scripts/provision_inventario_s3_bucket.py`.
6. Atualizar `register_inventory_task_definition.py` para injetar envs S3 e `taskRoleArn`.

## Resultado

- Bucket `inventario-remobs` criado e endurecido.
- Objeto marcador `remobs-inventario/.keep` gravado.
- Role de task ECS criada e autorizada no prefixo do bucket.
- Código pronto para gravar/ler/apagar anexos no S3.

## Pendente para produção efetiva

Publicar nova imagem Docker com o código S3 + `boto3` e registrar task definition com:

- `taskRoleArn = arn:aws:iam::220790920077:role/remobs-inventario-backend-task-role`
- `REMOBS_STORAGE_BACKEND=s3`
- `REMOBS_STORAGE_S3_BUCKET=inventario-remobs`
- `REMOBS_STORAGE_S3_REGION=sa-east-1`
- `REMOBS_STORAGE_S3_PREFIX=remobs-inventario`

Depois atualizar o serviço ECS `remobs-inventario-backend`.
