# Enriquecer plataformas PNBOIA com metadados, cascos, sistemas e sensores

## Objetivo
Preencher, para todas as boias importadas, os metadados detalhados da API PNBOIA e criar cascos, sistemas e sensores no inventário.

## Fonte
- `GET /v1/info/available_buoys`
- `GET /v1/info/metadata?buoy_id={id}&response_type=json`

## Mapeamento
| Destino | Origem |
|---|---|
| Platform.manufacturer/model | `boia.fabricante` / `boia.modelo` |
| Platform.description | fundeio + boia + histórico + contagens |
| Hull | código `PNBOIA-HULL-{id}`, modelo, diâmetro, peso |
| Systems | Fundeio, Estrutura da boia, Aquisição de dados, Histórico operacional |
| Sensors | `sensores{}` agrupados (anemômetro/ADCP/etc.) ou fallback por famílias de `parametros` + instalação ativa |

## Resultado produção
- 45 plataformas atualizadas
- 45 cascos
- 179 sistemas
- 175 sensores vinculados
- 1 boia com erro de metadata na API (HTTP 500 no buoy_id 11) — importada sem metadata detalhado
