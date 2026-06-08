# Planejamento de produção AWS para o REMOBS Inventário

## Contexto

O sistema REMOBS Inventário já possui backend FastAPI e frontend React/Vite, mas ainda não está 100% operacional em produção. O teste integrado confirmou que:

- O login no autenticador de produção funciona.
- O JWT emitido pelo controle de usuários é aceito quando o backend do inventário usa o mesmo segredo, issuer e audience.
- O backend do inventário responde ao healthcheck em `/healthz`.
- As rotas operacionais ainda falham no RDS porque o banco dedicado do inventário e suas tabelas ainda não foram criados.

A tarefa solicitada é planejar a entrada em produção com backend em Amazon ECS, frontend em AWS Amplify e rota pública `inventario.remobs.com.br`.

## Estado da AWS após execução parcial

- Os perfis AWS `default` e `api-mares` autenticaram na conta REMOBS.
- O RDS PostgreSQL existente identificado está disponível e será usado para hospedar o banco dedicado do inventário.
- O load balancer compartilhado `remobs-shared-api-alb` está ativo e foi mantido como entrada HTTP/HTTPS da API.
- O repositório ECR `remobs-inventario-backend` foi criado, com scan on push e lifecycle policy.
- A imagem Docker do backend foi publicada no ECR com as tags `prod-2026-06-08-inicial` e `latest`.
- O security group `remobs-inventario-backend-sg` foi criado para as tasks ECS, aceitando a porta `8000` apenas a partir do security group do load balancer compartilhado.
- O target group `tg-remobs-inventario-8000` foi criado com target type `ip` e healthcheck `/healthz`.
- O log group `/ecs/remobs-inventario-backend` foi criado com retenção de 30 dias.
- O certificado ACM para `api-inventario.remobs.com.br` foi solicitado, validado por DNS no Route 53 e anexado ao listener HTTPS existente.
- A regra HTTPS de prioridade `50` foi criada para encaminhar `api-inventario.remobs.com.br` ao target group do inventário.
- Nenhum registro público `inventario.remobs.com.br` ou `api-inventario.remobs.com.br` foi criado ainda, para evitar publicar rota sem serviço saudável.
- Nenhum ECS service foi criado ainda, mas o task definition `remobs-inventario-backend:2` já foi registrado com `REMOBS_DATABASE_URL`, `REMOBS_DATABASE_SSL=require` e JWT compatível com o controle de usuários.
- Nenhum app Amplify foi criado porque o código local ainda não foi commitado/pushado e o deploy conectado ao GitHub depende da branch de produção confirmada.
- Nenhuma migration foi executada no RDS nesta etapa.
- O banco dedicado `remobs_inventario` foi criado no RDS existente.
- O usuário dedicado `remobs_inventario_app` foi criado e validado com permissão para criar/remover tabela de teste no banco dedicado.
- A regra temporária no security group do RDS para o IP público local foi removida após o provisionamento.
- A imagem `prod-2026-06-08-banco` foi publicada no ECR com suporte explícito a `REMOBS_DATABASE_SSL=require`.

## Objetivo

Deixar o sistema operacional em produção com:

- Backend do inventário publicado em ECS/Fargate.
- Imagem Docker do backend armazenada no ECR.
- Variáveis sensíveis protegidas no mecanismo de segredos já adotado no ambiente REMOBS.
- Banco PostgreSQL dedicado no RDS existente, com usuário próprio para este banco.
- Frontend publicado no AWS Amplify.
- Domínio `inventario.remobs.com.br` apontando para o frontend.
- API do inventário acessível por domínio HTTPS próprio.
- Logs, healthcheck, rollback e validação operacional mínima antes de liberar uso.
- Sem criação de novo load balancer, novo RDS, nova hosted zone ou novo certificado pago.
- Custos novos previstos somente com o novo serviço ECS/Fargate, o repositório/armazenamento ECR e o app Amplify.

## Arquitetura proposta

### Backend

- Serviço: Amazon ECS com Fargate.
- Imagem: Amazon ECR.
- Entrada HTTP: load balancer já existente no ambiente REMOBS, com nova regra de roteamento para a API do inventário.
- Porta do container: `8000`.
- Healthcheck: `GET /healthz`.
- Logs: CloudWatch Logs.
- Segredos: reutilizar o mecanismo de segredos já implementado nos projetos irmãos; se o ambiente já usa Secrets Manager, injetar os valores no task definition do ECS a partir dele.
- Banco: novo database PostgreSQL no RDS existente, com usuário e senha próprios.
- Schema: não definir schema dedicado; usar o schema padrão `public` dentro do banco dedicado.

### Frontend

- Serviço: AWS Amplify Hosting.
- Fonte: repositório GitHub do projeto.
- Diretório base: `frontend/`.
- Build:
  - `npm ci`
  - `npm run build`
- Artefato: `frontend/dist`.
- Variáveis:
  - `VITE_AUTH_API_BASE_URL=https://api-controle-usuarios.remobs.com.br`
  - `VITE_INVENTARIO_API_BASE_URL=https://api-inventario.remobs.com.br`

### DNS

- `inventario.remobs.com.br`: apontar para o domínio do Amplify.
- `api-inventario.remobs.com.br`: apontar para o load balancer existente.
- Certificados TLS:
  - Amplify pode gerenciar o certificado do frontend.
  - A API deve usar o certificado já disponível no listener HTTPS do load balancer existente, ou incluir o novo SAN/domínio em certificado existente quando necessário.

## Restrições de custo

- Não criar novo RDS.
- Não criar novo load balancer.
- Não criar nova hosted zone.
- Não criar NAT Gateway novo.
- Não criar infraestrutura duplicada de rede.
- Custos novos permitidos:
  - novo serviço ECS/Fargate do inventário;
  - novo repositório e armazenamento ECR;
  - novo app/deploy do Amplify.
- Pode haver consumo variável indireto em recursos já existentes, como tráfego no load balancer e DNS, mas o plano não cria novos recursos pagos fora dos itens permitidos.

## Recursos AWS necessários

### ECR

- Repositório: `remobs-inventario-backend`.
- Política de lifecycle:
  - manter últimas 10 imagens;
  - remover imagens antigas sem tag.

### Segredos de produção

Nome lógico sugerido: `remobs/prod/inventario/backend`.

Não criar um segredo pago novo sem confirmação explícita. A ordem de preferência é:

1. Reutilizar o padrão de segredos já implementado no ambiente REMOBS.
2. Se já houver Secrets Manager em uso para os projetos irmãos, adicionar o inventário seguindo o mesmo padrão.
3. Se não houver mecanismo existente, registrar a decisão e pedir aprovação antes de criar recurso que gere custo adicional.

Chaves:

- `REMOBS_DATABASE_URL`
- `REMOBS_JWT_SECRET`
- `REMOBS_JWT_ISSUER`
- `REMOBS_JWT_AUDIENCE`
- `REMOBS_CORS_ORIGINS`

Valores não sensíveis no task definition:

- `REMOBS_ENVIRONMENT=prod`
- `REMOBS_DEBUG=false`
- `REMOBS_APP_NAME=remobs-inventario`
- Não definir `REMOBS_DATABASE_SCHEMA` em produção, pois o inventário usará banco dedicado e não schema dedicado.

### ECS/Fargate

- Cluster recomendado: `api-controle-usuarios-prod-cluster`, por já hospedar o backend de controle de usuários integrado ao JWT do inventário.
- Task family: `remobs-inventario-backend`.
- Service: `remobs-inventario-backend`.
- CPU/memória inicial: `0.25 vCPU` e `512 MB`.
- Desired count inicial: `1`.
- Subnets: reutilizar as subnets já usadas pelos serviços REMOBS existentes.
- Security groups:
  - Load balancer existente continua aceitando `443` da internet.
  - Task aceita `8000` apenas do security group do load balancer existente.
  - RDS aceita PostgreSQL apenas do security group da task.

### Load balancer existente

- Não criar novo load balancer.
- Reutilizar o load balancer já implementado no ecossistema REMOBS.
- Criar apenas o target group necessário para o ECS do inventário, se ainda não existir.
- Adicionar regra no listener HTTPS existente para `api-inventario.remobs.com.br`.
- Manter listener `80` existente com o comportamento já configurado no ambiente.
- Healthcheck: `/healthz`, matcher `200`.

### Amplify

- App: `remobs-inventario-frontend`.
- Branch inicial: branch de produção definida no GitHub.
- Build spec usando `frontend/` como base.
- Rewrites para SPA:
  - `/<*>` para `/index.html`, status `200`.
- Domínio customizado:
  - `inventario.remobs.com.br`.

### Route 53

- Hosted zone pública: `remobs.com.br`.
- Registros:
  - `inventario.remobs.com.br` para Amplify.
  - `api-inventario.remobs.com.br` como alias para o load balancer existente.

## Permissões AWS necessárias

O perfil que executará a implantação precisa, no mínimo:

- `sts:GetCallerIdentity`
- `ec2:DescribeVpcs`
- `ec2:DescribeSubnets`
- `ec2:DescribeSecurityGroups`
- `ec2:CreateSecurityGroup`
- `ec2:AuthorizeSecurityGroupIngress`
- `ec2:AuthorizeSecurityGroupEgress`
- `rds:DescribeDBInstances`
- Acesso administrativo PostgreSQL separado para criar o database dedicado e o usuário do inventário no RDS existente
- `ecs:RegisterTaskDefinition`, `ecs:CreateService`, `ecs:UpdateService`, `ecs:DescribeClusters`, `ecs:DescribeServices`, `ecs:DescribeTasks`, `ecs:ListClusters`, `ecs:ListServices` limitados ao cluster e serviços REMOBS
- `ecr:CreateRepository`, `ecr:DescribeRepositories`, `ecr:PutLifecyclePolicy`, `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage` limitados ao repositório do inventário
- `elasticloadbalancing:DescribeLoadBalancers`, `elasticloadbalancing:DescribeListeners`, `elasticloadbalancing:DescribeRules`, `elasticloadbalancing:DescribeTargetGroups`, `elasticloadbalancing:CreateTargetGroup`, `elasticloadbalancing:CreateRule`, `elasticloadbalancing:ModifyRule`, `elasticloadbalancing:RegisterTargets` limitados ao load balancer existente e ao target group do inventário
- `acm:ListCertificates`
- `acm:DescribeCertificate`
- `secretsmanager:DescribeSecret` e permissões equivalentes de leitura apenas se Secrets Manager já for o padrão existente do ecossistema
- Permissão de escrita/criação de segredo somente se houver aprovação explícita para eventual custo adicional
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `iam:PassRole`
- `logs:CreateLogGroup`
- `logs:PutRetentionPolicy`
- `amplify:*` limitado ao app do inventário
- `route53:ListHostedZones`
- `route53:ChangeResourceRecordSets`

## Fases de execução

### Fase 1: Desbloqueio de acesso AWS

Status: concluída.

1. Renovar login do perfil administrativo.
2. Validar identidade com `aws sts get-caller-identity`.
3. Confirmar região primária do backend.
4. Inventariar VPC, subnets, security groups, RDS, Route 53, ACM, ECS, ECR, Amplify, load balancer existente, listeners e regras já configuradas.
5. Registrar decisões de uso de VPC/subnets no plano antes de criar recursos.

### Fase 2: Preparação do backend para container

Status: concluída localmente.

1. Criar `backend/Dockerfile`.
2. Criar `backend/.dockerignore`.
3. Garantir comando de produção:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Validar build local da imagem.
5. Validar execução local do container com `/healthz`.

### Fase 3: Banco de dados

Status: banco e usuário concluídos; migration no RDS pendente de confirmação explícita.

1. Confirmar o nome do banco dedicado, sugerido como `remobs_inventario`. Status: concluído.
2. Confirmar o nome do usuário do banco, sugerido como `remobs_inventario_app`. Status: concluído.
3. Obter credencial administrativa PostgreSQL do RDS existente. Status: concluído a partir do arquivo de acesso local indicado pelo usuário.
4. Criar o banco dedicado no RDS existente, sem criar nova instância RDS e sem criar schema dedicado. Status: concluído.
5. Criar usuário próprio para a aplicação do inventário. Status: concluído.
6. Conceder ao usuário acesso apenas ao banco dedicado e aos objetos necessários no schema padrão `public`. Status: concluído e validado por tabela de teste.
7. Ajustar o backend antes da migration para não usar `REMOBS_DATABASE_SCHEMA=inventario` e para não criar o schema `inventario` na migration inicial. Status: concluído.
8. Confirmar explicitamente a execução de migration no RDS.
9. Fazer backup/snapshot antes da migration, quando possível.
10. Executar `alembic upgrade head` apontando `REMOBS_DATABASE_URL` para o banco dedicado `remobs_inventario`, sem variável de schema.
11. Validar existência das tabelas principais no banco dedicado:
   - `inventory_items`
   - `stock_balances`
   - `stock_movements`
   - `audit_logs`
   - `alerts`
   - `platforms`
   - `sensors`
12. Validar APIs com token real do `remobs-users`.

### Fase 4: ECR e ECS

Status: ECR, imagem, security group, target group, log group e task definition concluídos; ECS service pendente.

1. Criar repositório ECR `remobs-inventario-backend`.
2. Autenticar Docker no ECR.
3. Buildar e publicar imagem versionada.
4. Criar log group CloudWatch.
5. Criar roles ECS:
   - task execution role;
   - task role da aplicação.
6. Localizar o load balancer existente e o listener HTTPS já utilizado pelo ecossistema REMOBS.
7. Criar apenas o target group do inventário, se ainda não existir.
8. Criar regra no listener HTTPS existente para `api-inventario.remobs.com.br`.
9. Registrar task definition com referências aos segredos existentes ou ao mecanismo de configuração aprovado. Status: concluído na revisão `remobs-inventario-backend:2`.
10. Criar ECS service com Fargate no cluster existente.
11. Validar:
   - task está `RUNNING`;
   - target está `healthy`;
   - `/healthz` retorna `200` via load balancer existente;
   - endpoints autenticados funcionam com JWT real.

### Fase 5: Domínio da API

Status: certificado e regra do listener concluídos; DNS público pendente até o ECS service ficar saudável.

1. Confirmar se o certificado ACM já associado ao listener HTTPS existente cobre `api-inventario.remobs.com.br`.
2. Se necessário, atualizar certificado existente ou anexar certificado ACM compatível ao listener existente, sem criar novo load balancer.
3. Criar regra host-based no listener HTTPS existente para encaminhar `api-inventario.remobs.com.br` ao target group do inventário.
4. Criar registro Route 53 alias para o load balancer existente.
5. Validar:
   - `https://api-inventario.remobs.com.br/healthz`;
   - CORS com origem `https://inventario.remobs.com.br`.

### Fase 6: Amplify

Status: configuração local concluída; criação do app pendente de confirmação da branch de produção e commit/push do código.

1. Criar app Amplify conectado ao GitHub.
2. Configurar branch de produção.
3. Definir variáveis:
   - `VITE_AUTH_API_BASE_URL`
   - `VITE_INVENTARIO_API_BASE_URL`
4. Definir build spec com base em `frontend/`.
5. Configurar rewrite de SPA.
6. Fazer primeiro deploy.
7. Validar build, artefato e acesso no domínio padrão do Amplify.

### Fase 7: Domínio do frontend

1. Associar `inventario.remobs.com.br` ao app Amplify.
2. Criar/validar registros DNS necessários no Route 53.
3. Aguardar provisionamento TLS.
4. Validar:
   - acesso HTTPS;
   - login real;
   - navegação autenticada;
   - chamadas para `api-inventario.remobs.com.br`.

### Fase 8: Validação operacional

1. Executar testes automatizados:
   - backend;
   - frontend;
   - build do frontend.
2. Fazer smoke test em produção:
   - login;
   - `/users/me`;
   - listagem de inventário;
   - criação de item controlado de teste;
   - consulta de auditoria;
   - solicitação de movimentação;
   - aprovação/rejeição;
   - alertas;
   - sincronização.
3. Verificar logs CloudWatch.
4. Verificar métricas do load balancer existente e do ECS.
5. Validar responsividade mobile em produção.

## Atualização final da execução

Status em 2026-06-08: produção operacional.

Recursos concluídos:

- Banco dedicado `remobs_inventario` criado no RDS PostgreSQL existente, sem criação de schema dedicado.
- Usuário dedicado `remobs_inventario_app` criado e validado para o banco do inventário.
- Migration Alembic inicial executada no banco dedicado após autorização do usuário.
- Tabelas principais validadas, incluindo `inventory_items`, `stock_balances`, `stock_movements`, `audit_logs`, `alerts`, `platforms` e `sensors`.
- Imagem do backend publicada no ECR `remobs-inventario-backend`.
- ECS service `remobs-inventario-backend` criado no cluster existente `api-controle-usuarios-prod-cluster`.
- Target group `tg-remobs-inventario-8000` saudável no load balancer compartilhado.
- API publicada em `https://api-inventario.remobs.com.br`.
- App Amplify `remobs-inventario-frontend` criado e publicado na branch `prod`.
- Domínio `https://inventario.remobs.com.br` associado ao Amplify e validado por HTTPS.
- Rotas diretas do SPA corrigidas no artefato publicado, incluindo `/login/`, `/app/home/` e `/app/inventory/`.
- Favicon e autocomplete da tela de login ajustados para eliminar ruídos de console em produção.

Validações finais executadas:

- `python -m pytest backend/tests -q`: 7 testes aprovados.
- `npm test -- --run`: 4 arquivos e 9 testes aprovados.
- `npm run build`: build Vite/TypeScript aprovado.
- `https://api-inventario.remobs.com.br/healthz`: retorno `{"status":"ok"}`.
- Target health do load balancer: `healthy`.
- `https://inventario.remobs.com.br/login/`: HTTP `200`.
- `https://inventario.remobs.com.br/app/inventory/`: HTTP `200`.
- Smoke test autenticado com o usuário informado pelo usuário:
  - login;
  - `/users/me`;
  - listagem de inventário;
  - criação de item controlado de teste;
  - consulta do item;
  - histórico;
  - solicitação de movimentação;
  - rejeição da movimentação;
  - listagem de movimentações;
  - alertas;
  - plataformas;
  - sensores;
  - status de sincronização;
  - logs de auditoria;
  - exclusão do item de teste.
- Login real no navegador com o frontend publicado, confirmando chamadas para `https://api-controle-usuarios.remobs.com.br` e `https://api-inventario.remobs.com.br`, todas com status `200`.
- Validação visual responsiva em 360px, 390px, 430px e 1440px, sem erros ou warnings de console.

Observações:

- Os itens criados pelo smoke test foram removidos ao final de cada execução.
- Os registros de auditoria e movimentações rejeitadas permanecem no banco por desenho append-only.
- Não foi criado novo RDS, novo load balancer, nova hosted zone ou novo schema dedicado.
- Os custos novos seguem restritos aos recursos autorizados: ECS/Fargate, ECR e Amplify, além do uso incremental dos recursos compartilhados existentes.

## Comandos previstos

Os comandos abaixo devem ser executados apenas após a sessão AWS administrativa estar válida.

```powershell
aws sts get-caller-identity --profile <perfil-admin>
aws ec2 describe-vpcs --profile <perfil-admin> --region sa-east-1
aws rds describe-db-instances --profile <perfil-admin> --region sa-east-1
aws route53 list-hosted-zones --profile <perfil-admin>
aws acm list-certificates --profile <perfil-admin> --region sa-east-1
aws ecs list-clusters --profile <perfil-admin> --region sa-east-1
aws ecs describe-clusters --clusters api-controle-usuarios-prod-cluster --profile <perfil-admin> --region sa-east-1
aws elbv2 describe-load-balancers --profile <perfil-admin> --region sa-east-1
aws elbv2 describe-listeners --load-balancer-arn <arn-load-balancer-existente> --profile <perfil-admin> --region sa-east-1
aws elbv2 describe-rules --listener-arn <arn-listener-https-existente> --profile <perfil-admin> --region sa-east-1
aws ecr create-repository --repository-name remobs-inventario-backend --profile <perfil-admin> --region sa-east-1
```

Criação do banco dedicado e do usuário próprio no RDS existente deve ocorrer somente com confirmação explícita:

```sql
CREATE ROLE remobs_inventario_app LOGIN PASSWORD '<senha-gerada>';
CREATE DATABASE remobs_inventario;
REVOKE ALL ON DATABASE remobs_inventario FROM PUBLIC;
GRANT CONNECT ON DATABASE remobs_inventario TO remobs_inventario_app;

\connect remobs_inventario
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO remobs_inventario_app;
```

Migration no RDS só deve ocorrer com confirmação explícita e depois de remover o uso de schema dedicado no código:

```powershell
$env:REMOBS_DATABASE_URL="postgresql+asyncpg://remobs_inventario_app:<senha>@<endpoint-rds>:5432/remobs_inventario"
Remove-Item Env:\REMOBS_DATABASE_SCHEMA -ErrorAction SilentlyContinue
python -m alembic -c backend/alembic.ini upgrade head
```

## Riscos e decisões pendentes

- A migration atual é PostgreSQL-first e não deve ser usada em SQLite local para simular produção.
- O código foi ajustado para usar banco dedicado com schema padrão `public`, sem criação de schema `inventario` em produção.
- O domínio da API deve ser separado do frontend para evitar conflito com Amplify.
- A URL de produção do frontend foi configurada como `VITE_INVENTARIO_API_BASE_URL=https://api-inventario.remobs.com.br`.
- É necessário confirmar a branch GitHub de produção.
- A migration no RDS ainda precisa de confirmação explícita antes de executar `alembic upgrade head`.
- O plano agora recomenda usar o cluster ECS existente do controle de usuários.
- O cliente `psql` não está instalado localmente; a criação do banco dedicado pode ser feita por cliente SQL externo ou script Python controlado, mas ainda depende de confirmação explícita.
- O app Amplify e o domínio `inventario.remobs.com.br` dependem de commit/push do código e da branch de produção confirmada.

## Referências oficiais consultadas

- AWS Amplify Hosting permite conectar app hospedado a domínio customizado e usar certificado gerenciado ou ACM.
- Amazon ECS/Fargate pode receber segredos do Secrets Manager como variáveis de ambiente do container.
- Route 53 pode criar alias record para load balancers do Elastic Load Balancing, incluindo subdomínios.
- O Amazon RDS permite múltiplos bancos criados pelo usuário dentro de uma mesma instância PostgreSQL, com acesso via cliente SQL padrão.
- O Amazon ECS permite usar Elastic Load Balancing com serviços Fargate e associar serviços a target groups.

Fontes:

- https://docs.aws.amazon.com/amplify/latest/userguide/custom-domains.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.DBInstance.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.Access.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html

## Resultado

Implementação de produção concluída e validada em 2026-06-08. O backend está publicado em ECS/Fargate atrás do load balancer existente, a API responde em `https://api-inventario.remobs.com.br`, o frontend está publicado no Amplify em `https://inventario.remobs.com.br`, o banco dedicado existe no RDS com usuário próprio e a migration inicial foi aplicada. O fluxo autenticado foi validado com usuário real, incluindo criação e remoção de item controlado, movimentação rejeitada, auditoria, alertas, plataformas, sensores e sincronização.
