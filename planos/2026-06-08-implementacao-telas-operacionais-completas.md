# Implementação das Telas Operacionais Completas

## Contexto

O sistema REMOBS Inventário possui uma base funcional com autenticação, inventário, movimentações, plataformas, sensores, sincronização e logs. A análise das telas planejadas mostrou que parte dos fluxos ainda está simplificada ou ausente.

O usuário solicitou implementar as telas operacionais pendentes e remover do planejamento as telas administrativas e os fluxos de recuperação de senha, pois não farão parte deste sistema.

## Objetivo

Implementar os seguintes fluxos no frontend e, quando necessário, completar os contratos do backend:

- Checklist de campo;
- Detalhe de plataforma;
- Detalhe de sensor;
- Resolução de conflito offline;
- Dashboard completo;
- Inventário completo;
- Solicitação de saída completa.

Também será atualizada a documentação de planejamento para remover telas administrativas e esqueci senha/reset senha.

## Escopo

Incluído:

- Novas rotas autenticadas para checklists, detalhe de plataforma e detalhe de sensor;
- Melhorias nas telas existentes de dashboard, inventário, solicitação de saída e sincronização;
- Contratos backend para consultas agregadas e ações necessárias aos fluxos;
- Testes de contrato backend e testes frontend de navegação/API;
- Atualização de `CHANGELOG.md`;
- Commits separados por bloco lógico.

Fora do escopo:

- Tela administrativa de usuários, papéis, permissões, logs administrativos e relatórios administrativos;
- Fluxos públicos de esqueci senha e reset senha;
- Integrações reais de câmera, QR Code, upload de arquivo e armazenamento offline persistente no backend além da fila/sincronização já prevista;
- Migrações destrutivas ou execução de migrações em banco de produção.

## Abordagem Técnica

### Backend

1. Adicionar leitura detalhada de plataformas com casco, sistemas e sensores vinculados.
2. Adicionar leitura detalhada de sensores com plataforma atual e histórico básico.
3. Criar módulo simples de checklists com persistência própria.
4. Ampliar sincronização para listar pendências/conflitos e registrar decisões de resolução.
5. Manter padrões existentes de FastAPI, SQLAlchemy assíncrono, Pydantic v2 e auditoria.

### Frontend

1. Adicionar tipos e métodos no `inventoryService`.
2. Criar páginas de checklists, detalhe de plataforma e detalhe de sensor.
3. Melhorar dashboard com indicadores operacionais.
4. Melhorar inventário com busca, filtros, resumo, histórico e campos adicionais.
5. Melhorar solicitação de saída com validação de estoque, rascunho local e confirmação.
6. Melhorar sincronização com lista de pendências, conflitos e ações.
7. Manter Material UI e React Router conforme padrões existentes.

## Etapas

1. Criar plano e commit separado.
2. Escrever testes backend que falhem para os novos contratos.
3. Implementar modelos, schemas e rotas backend.
4. Rodar testes backend e criar commit backend.
5. Escrever testes frontend que falhem para navegação e cliente API.
6. Implementar tipos, serviços, rotas e telas frontend.
7. Rodar testes frontend e build.
8. Atualizar documentação de planejamento removendo admin e recuperação de senha.
9. Atualizar changelog.
10. Criar commit de documentação.
11. Executar validação final completa.

## Validações

- `pytest` no backend;
- `npm test -- --run` no frontend;
- `npm run build` no frontend;
- Revisão de rotas e documentação para confirmar remoção de admin e esqueci senha/reset senha;
- Revisão de `git diff` antes de cada commit.

## Resultado Esperado

Ao final, o sistema terá os principais fluxos operacionais implementados, com telas navegáveis, contratos backend compatíveis, documentação coerente com o escopo real e commits separados por tipo de alteração.
