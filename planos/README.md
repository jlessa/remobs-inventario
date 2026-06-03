# REMOBS — Planos em Markdown

Este pacote organiza o plano de implementação e o plano de design das telas do sistema de inventário e acompanhamento do projeto REMOBS.

O material foi estruturado a partir dos módulos levantados nas anotações:

- **Controle de Material**
  - Consumíveis
  - Componentes permanentes
  - Estoque, locais, saída, nota fiscal, fotos e vínculo patrimonial
- **Gerenciamento e Acompanhamento**
  - Plataformas fixas e móveis
  - Cascos, sistemas embarcados, sensores, documentação e status operacional
- **Usuários e permissões**
  - Desenvolvedor, Administrador, Operação, DGAes e papéis complementares
- **Uso em campo**
  - Operação em celular, com experiência mobile-first, MUI/Material UI e suporte a baixa conectividade

## Estrutura dos arquivos

```text
remobs_planos_md/
├── README.md
├── implementacao/
│   ├── 01-plano-geral-implementacao.md
│   ├── 02-login-permissoes-sessoes.md
│   ├── 03-logs-auditoria-observabilidade.md
│   ├── 04-modelagem-dados-api.md
│   ├── 05-modulos-inventario-operacao.md
│   └── 06-roadmap-sprints-criterios.md
└── design/
    ├── 01-design-system-mobile-first-material-ui.md
    ├── 02-arquitetura-telas-navegacao.md
    ├── 03-telas-operacao-campo.md
    ├── 04-telas-admin-permissoes-logs.md
    ├── 05-padroes-formularios-listas.md
    └── 06-prototipo-fluxos-principais.md
```

## Diretrizes centrais

1. **Mobile-first:** o sistema deve ser pensado primeiro para celulares usados em campo.
2. **Operação robusta:** formulários devem salvar rascunhos, permitir fila offline e sincronização posterior.
3. **Rastreabilidade:** toda alteração crítica deve gerar log de auditoria.
4. **Permissões claras:** cada usuário deve enxergar somente o que pode consultar ou alterar.
5. **Inventário técnico:** consumíveis, componentes permanentes, sensores, cascos e plataformas devem ter histórico completo.
6. **Material UI:** utilizar componentes MUI com adaptação responsiva, evitando tabelas largas em telas pequenas.

## Premissas técnicas sugeridas

A stack pode ser adaptada, mas o plano assume a seguinte base para facilitar a implementação:

- Frontend: **React + TypeScript + Material UI**
- Aplicação de campo: **PWA responsiva**, instalável no celular
- Backend: **API REST** ou **GraphQL**, com autenticação por token
- Banco de dados: **PostgreSQL**
- Armazenamento de arquivos: bucket compatível com S3, MinIO ou serviço equivalente
- Cache/fila: Redis ou mecanismo equivalente para notificações e sincronização
- Logs: tabelas de auditoria no banco + logs técnicos centralizados

## Resultado esperado

Um sistema único para controlar materiais, acompanhar plataformas e registrar operações de campo, com experiência adequada para celular e com segurança, permissões e logs desde a primeira versão.
