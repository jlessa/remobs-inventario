# Apagar itens permanentes fora da lista permitida em produção

## Contexto

O inventário de produção possui muitos componentes permanentes importados das planilhas. A operação pediu manter apenas os permanentes cujo **nome** seja um dos tipos permitidos e soft-excluir o restante.

## Objetivo

Em produção, soft-delete de todos os itens com `item_type = permanent_component` ativos cujo nome **não** esteja na allowlist:

- ACDC
- LANTERNA
- PAINEL SOLAR
- ESTAÇÃO METEOROLÓGICA
- PLUVIOMETRO
- ANEMOMETRO

## Escopo

- Apenas `inventory_items` com `item_type = 'permanent_component'` e `deleted_at IS NULL`
- Comparação pelo **nome** do item (normalizado: maiúsculas, sem acento, espaços colapsados)
- Soft delete (`is_active = false`, `deleted_at = now()`, `row_version += 1`) + log de auditoria
- **Não** apaga consumíveis (`consumable`)
- **Não** hard delete (preserva FK de saldos, movimentos e arquivos)

## Fora do escopo

- Exclusão física de linhas no banco
- Alteração de sensores/plataformas
- Recarga de planilhas

## Ambiente alvo

- Profile AWS: `aws-remobs` (conta `220790920077`)
- Região: `sa-east-1`
- Banco: `remobs_inventario` via `REMOBS_DATABASE_URL` do task definition ECS do backend

## Regra de matching (confirmada no plano)

Manter se `normalize(name)` for **igual** a um dos nomes da allowlist (não usa contains).

Exemplos:

| Nome no banco | Ação |
|---|---|
| `Anemômetro` | manter |
| `Peças Anemômetro` | apagar |
| `Painel Solar` | manter |
| `Cabo painel solar` | apagar |
| `Rain Gauge` | apagar (não é o nome `PLUVIOMETRO`) |
| `Weather Station` | apagar (não é `ESTAÇÃO METEOROLÓGICA`) |

## Etapas

1. Analisar planilha local para estimar volumes (feito).
2. Criar script `backend/scripts/cleanup_permanent_items_allowlist.py` com `--dry-run` (padrão) e `--apply`.
3. Dry-run em produção (somente leitura + relatório de contagens por nome).
4. Confirmação explícita do usuário para `--apply`.
5. Soft-delete em produção + validação de contagens.
6. Atualizar `CHANGELOG.md`.

## Estimativa local (planilha, não produção)

Permanentes na planilha: ~606.

Match exato allowlist na planilha:

| Nome normalizado | Qtd |
|---|---:|
| ANEMOMETRO | 42 |
| PAINEL SOLAR | 41 |
| LANTERNA | 19 |
| ESTACAO METEOROLOGICA | 4 |
| ACDC | 0 |
| PLUVIOMETRO | 0 |
| **Total manter** | **~106** |
| **Estimativa apagar** | **~500** |

Observação: `ACDC` e `PLUVIOMETRO` não aparecem com esse nome exato na planilha local; em produção o dry-run decide o número real.

## Resultado

Concluído em 2026-08-06.

- Profile: `aws-remobs` / região `sa-east-1`
- Soft-delete via `backend/scripts/cleanup_permanent_items_allowlist.py --apply --yes`
- Permanentes ativos antes: **564**
- Soft-deletados: **533**
- Permanentes ativos depois: **31**
  - PAINEL SOLAR: 16
  - LANTERNA: 6
  - ANEMOMETRO: 3
  - ESTAÇÃO METEOROLÓGICA: 3
  - PLUVIOMETRO: 3
  - ACDC: 0 (não existia em produção)
- Candidatos restantes fora da allowlist: **0**
- Auditoria: 533 entradas `inventory_item_deleted` (source `script`)

## Correção — restore ADCP

Usuário pediu restore dos ADCP apagados por engano (nome `ADCP` ≠ allowlist `ACDC`).

- Script: `backend/scripts/restore_soft_deleted_adcp.py --apply --yes`
- Restaurados: **11** ADCP (9 da limpeza de 2026-08-06 + 2 já soft-deletados em 2026-08-05)
- ADCP soft-deletados restantes: **0**
- Permanentes ativos após restore: **42** (31 allowlist + 11 ADCP)
- Auditoria: 11 entradas `inventory_item_restored` (source `script`)

## Correção — restore Unidade de Comando

- Script genérico: `backend/scripts/restore_soft_deleted_by_name.py --name "Unidade de Comando" --apply --yes`
- Restaurados: **3** (seriais `MO 1221`, `MO 01321`, `MO01021`)
- Soft-deletados restantes com esse nome: **0**
- Permanentes ativos após restore: **45**
