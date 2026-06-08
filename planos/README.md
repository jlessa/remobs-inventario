# REMOBS — Planos em Markdown

Este pacote organiza o plano de implementação e o plano de design das telas do sistema de inventário e acompanhamento do projeto REMOBS.

O material está focado no sistema operacional de inventário, acompanhamento de plataformas e uso em campo. Telas administrativas de usuários, papéis, permissões, relatórios administrativos e recuperação de senha não fazem parte deste sistema.

## Módulos

- **Controle de Material**
  - Consumíveis
  - Componentes permanentes
  - Estoque, locais, saída, nota fiscal, fotos e vínculo patrimonial
- **Gerenciamento e Acompanhamento**
  - Plataformas fixas e móveis
  - Cascos, sistemas embarcados, sensores, documentação e status operacional
- **Uso em campo**
  - Operação em celular, experiência mobile-first, MUI/Material UI, checklists, rascunhos e baixa conectividade
- **Sincronização operacional**
  - Pendências offline, conflitos, decisão do usuário e registro de auditoria técnica

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
    ├── 05-padroes-formularios-listas.md
    └── 06-prototipo-fluxos-principais.md
```

## Diretrizes centrais

1. **Mobile-first:** o sistema deve ser pensado primeiro para celulares usados em campo.
2. **Operação robusta:** formulários devem salvar rascunhos, permitir fila offline e sincronização posterior.
3. **Rastreabilidade:** toda alteração crítica deve gerar log de auditoria técnica.
4. **Permissões claras:** cada usuário deve enxergar somente o que pode consultar ou alterar nos módulos operacionais.
5. **Inventário técnico:** consumíveis, componentes permanentes, sensores, cascos e plataformas devem ter histórico completo.
6. **Material UI:** utilizar componentes MUI com adaptação responsiva, evitando tabelas largas em telas pequenas.

## Premissas técnicas sugeridas

- Frontend: **React + TypeScript + Material UI**
- Aplicação de campo: **PWA responsiva**, instalável no celular
- Backend: **API REST**, com autenticação por token emitido pelo projeto de usuários do ecossistema
- Banco de dados: **PostgreSQL**
- Armazenamento de arquivos: bucket compatível com S3, MinIO ou serviço equivalente
- Cache/fila: Redis ou mecanismo equivalente para notificações e sincronização
- Logs: tabelas de auditoria no banco e logs técnicos centralizados

## Resultado esperado

Um sistema único para controlar materiais, acompanhar plataformas e registrar operações de campo, com experiência adequada para celular, segurança, permissões operacionais e logs desde a primeira versão.
