from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_PNBOIA_BASE_URL = "http://dados.pnboia.org"
DEFAULT_PNBOIA_TOKEN = "JXlFe-ybjfGGJgJRpKfa"
IMPORT_MARKER_PREFIX = "remobs-import:pnboia-buoy:"
HULL_CODE_PREFIX = "PNBOIA-HULL-"
SENSOR_MARKER_PREFIX = "remobs-import:pnboia-sensor:"

ACTIVE_OPERATIONAL_STATUSES = frozenset({"em_operacao", "disponivel"})


def map_operational_status(*, is_active: bool, mode: str | None) -> str:
    if is_active:
        return "em_operacao"
    normalized = (mode or "").strip().upper()
    mapping = {
        "INOPERANTE": "inoperante",
        "MANUTENCAO": "manutencao",
        "DERIVANDO": "derivando",
        "DERIVA": "derivando",
        "GAP": "offline",
        "FUNDEADA": "inativa",
        "LANCAMENTO": "planejamento",
        "RECOLHIMENTO": "manutencao",
    }
    return mapping.get(normalized, "inativa")


def map_hull_status(mode: str | None, *, is_active: bool) -> str:
    if is_active:
        return "em_operacao"
    return map_operational_status(is_active=False, mode=mode)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _slug(value: str, max_len: int = 80) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return (text or "item")[:max_len]


def build_description(buoy: dict[str, Any], metadata: dict[str, Any] | None = None) -> str:
    meta = metadata or {}
    boia = meta.get("boia") if isinstance(meta.get("boia"), dict) else {}
    fundeio = meta.get("fundeio") if isinstance(meta.get("fundeio"), dict) else {}
    historico = meta.get("historico") if isinstance(meta.get("historico"), dict) else {}
    sensores = meta.get("sensores") if isinstance(meta.get("sensores"), dict) else {}
    parametros = meta.get("parametros") if isinstance(meta.get("parametros"), dict) else {}

    lines = [
        "Origem: API PNBOIA /v1/info/available_buoys + /v1/info/metadata.",
        f"{IMPORT_MARKER_PREFIX}{buoy['buoy_id']}",
        f"buoy_id: {buoy['buoy_id']}",
        f"is_active: {'true' if buoy.get('is_active') else 'false'}",
    ]

    for label, value in [
        ("name", buoy.get("name") or meta.get("nome")),
        ("type", buoy.get("type")),
        ("mode", buoy.get("mode") or meta.get("situacao")),
        ("api_endpoint", buoy.get("api_endpoint") or meta.get("api_endpoint")),
        ("last_date_time", buoy.get("last_date_time")),
        ("metarea_section", buoy.get("metarea_section")),
        ("project_id", buoy.get("project_id")),
        ("fabricante", boia.get("fabricante")),
        ("modelo", boia.get("modelo")),
        ("diametro_m", boia.get("diametro (m)")),
        ("peso_kg", boia.get("peso (kg)")),
        ("local", fundeio.get("local") or buoy.get("local")),
        ("latitude", fundeio.get("latitude") if fundeio.get("latitude") is not None else buoy.get("latitude")),
        ("longitude", fundeio.get("longitude") if fundeio.get("longitude") is not None else buoy.get("longitude")),
        ("profundidade_fundeio_m", fundeio.get("pofundidade de fundeio (m)")),
        ("qtd_parametros", len(parametros) if parametros else 0),
        ("qtd_atributos_sensores", len(sensores) if sensores else 0),
        ("qtd_periodos_historico", len(historico) if historico else 0),
    ]:
        if value not in (None, ""):
            lines.append(f"{label}: {value}")

    if historico:
        lines.append("historico:")
        for key, period in list(historico.items())[:12]:
            if not isinstance(period, dict):
                continue
            modo = period.get("modo")
            inicio = period.get("inicio")
            fim = period.get("fim")
            duracao = period.get("duracao (dias)")
            lines.append(f"  - {key}: {modo} ({inicio} → {fim}" + (f", {duracao} dias" if duracao is not None else "") + ")")

    return "\n".join(lines)


def build_hull_payload(buoy: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = metadata or {}
    boia = meta.get("boia") if isinstance(meta.get("boia"), dict) else {}
    mode = str(buoy.get("mode") or meta.get("situacao") or "")
    notes_parts = []
    for label, key in [
        ("Diâmetro (m)", "diametro (m)"),
        ("Peso (kg)", "peso (kg)"),
        ("Fabricante", "fabricante"),
        ("Modelo", "modelo"),
    ]:
        value = boia.get(key)
        if value not in (None, ""):
            notes_parts.append(f"{label}: {value}")
    notes_parts.append(f"{IMPORT_MARKER_PREFIX}{buoy['buoy_id']}")
    return {
        "code": f"{HULL_CODE_PREFIX}{buoy['buoy_id']}",
        "model": _clean(boia.get("modelo")) or _clean(buoy.get("type")),
        "status": map_hull_status(mode, is_active=bool(buoy.get("is_active"))),
        "notes": "\n".join(notes_parts),
    }


def build_systems_payload(buoy: dict[str, Any], metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    meta = metadata or {}
    boia = meta.get("boia") if isinstance(meta.get("boia"), dict) else {}
    fundeio = meta.get("fundeio") if isinstance(meta.get("fundeio"), dict) else {}
    historico = meta.get("historico") if isinstance(meta.get("historico"), dict) else {}
    parametros = meta.get("parametros") if isinstance(meta.get("parametros"), dict) else {}
    sensores = meta.get("sensores") if isinstance(meta.get("sensores"), dict) else {}
    status = "operacional" if buoy.get("is_active") else "inativo"

    systems: list[dict[str, Any]] = []

    fundeio_notes = []
    for label, key in [
        ("Local", "local"),
        ("Latitude", "latitude"),
        ("Longitude", "longitude"),
        ("Profundidade (m)", "pofundidade de fundeio (m)"),
    ]:
        value = fundeio.get(key)
        if value is None and key in {"local", "latitude", "longitude"}:
            value = buoy.get(key)
        if value not in (None, ""):
            fundeio_notes.append(f"{label}: {value}")
    systems.append(
        {
            "name": "Fundeio",
            "status": status,
            "notes": "\n".join(fundeio_notes) if fundeio_notes else "Sem dados de fundeio na API.",
        }
    )

    estrutura_notes = []
    for label, key in [
        ("Fabricante", "fabricante"),
        ("Modelo", "modelo"),
        ("Diâmetro (m)", "diametro (m)"),
        ("Peso (kg)", "peso (kg)"),
    ]:
        value = boia.get(key)
        if value not in (None, ""):
            estrutura_notes.append(f"{label}: {value}")
    systems.append(
        {
            "name": "Estrutura da boia",
            "status": status,
            "notes": "\n".join(estrutura_notes) if estrutura_notes else "Sem metadados estruturais na API.",
        }
    )

    api_endpoint = buoy.get("api_endpoint") or meta.get("api_endpoint")
    aquisicao_notes = [
        f"Endpoint de dados: {api_endpoint}" if api_endpoint else "Endpoint de dados não informado.",
        f"Parâmetros catalogados: {len(parametros)}",
        f"Atributos de sensores: {len(sensores)}",
    ]
    systems.append(
        {
            "name": "Aquisição de dados",
            "status": status,
            "notes": "\n".join(aquisicao_notes),
        }
    )

    if historico:
        hist_lines = []
        for key, period in list(historico.items())[:20]:
            if not isinstance(period, dict):
                continue
            hist_lines.append(
                f"{key}: {period.get('modo')} ({period.get('inicio')} → {period.get('fim')})"
            )
        systems.append(
            {
                "name": "Histórico operacional",
                "status": status,
                "notes": "\n".join(hist_lines) if hist_lines else "Histórico vazio.",
            }
        )

    return systems


def _infer_sensor_type(label: str) -> tuple[str, str]:
    lower = label.casefold()
    if "anem" in lower or "vento" in lower or "wind" in lower:
        return "anemometro", "Anemômetro"
    if "adcp" in lower or "corrente" in lower:
        return "adcp", "ADCP"
    if "onda" in lower or "wave" in lower or "swvht" in lower or "triaxys" in lower:
        return "ondografo", "Ondógrafo"
    if "temp" in lower or "sst" in lower:
        return "termometro", "Termômetro"
    if "press" in lower or "baro" in lower:
        return "barometro", "Barômetro"
    if "gps" in lower or "lat" in lower or "lon" in lower:
        return "gnss", "GNSS"
    if "spotter" in lower:
        return "spotter", "Spotter"
    return "sensor", "Sensor"


def build_sensors_payload(buoy: dict[str, Any], metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    meta = metadata or {}
    boia = meta.get("boia") if isinstance(meta.get("boia"), dict) else {}
    sensores = meta.get("sensores") if isinstance(meta.get("sensores"), dict) else {}
    parametros = meta.get("parametros") if isinstance(meta.get("parametros"), dict) else {}
    brand = _clean(boia.get("fabricante")) or _clean(buoy.get("type"))
    model = _clean(boia.get("modelo")) or _clean(buoy.get("type"))
    status = "operacional" if buoy.get("is_active") else "inoperante"
    buoy_id = int(buoy["buoy_id"])
    sensors: list[dict[str, Any]] = []

    if sensores:
        # Agrupa atributos por família lógica (anemômetro 1, adcp, etc.)
        groups: dict[str, list[tuple[str, Any]]] = {}
        for key, value in sensores.items():
            sensor_type, family = _infer_sensor_type(str(key))
            # tenta extrair "sensor N"
            match = re.search(r"sensor\s*(\d+)", str(key), flags=re.IGNORECASE)
            group_key = f"{family}-{match.group(1)}" if match else family
            groups.setdefault(group_key, []).append((str(key), value))

        for group_key, attrs in groups.items():
            family = group_key.rsplit("-", 1)[0] if re.search(r"-\d+$", group_key) else group_key
            sensor_type, family_label = _infer_sensor_type(family)
            notes = "\n".join(f"{k}: {v}" for k, v in attrs)
            serial = f"PNBOIA-{buoy_id}-{_slug(group_key)}"
            sensors.append(
                {
                    "sensor_type": sensor_type,
                    "family": family_label[:120],
                    "brand": brand,
                    "model": model,
                    "serial_number": serial[:160],
                    "operational_status": status,
                    "notes": f"{SENSOR_MARKER_PREFIX}{buoy_id}:{_slug(group_key)}\n{notes}",
                    "installation_notes": f"Configuração importada da API PNBOIA para boia {buoy_id}.",
                    "marker": f"{SENSOR_MARKER_PREFIX}{buoy_id}:{_slug(group_key)}",
                }
            )
        return sensors

    # Fallback: cria sensores lógicos a partir de famílias de parâmetros.
    families: dict[str, list[str]] = {}
    for key, description in parametros.items():
        sensor_type, family_label = _infer_sensor_type(f"{key} {description}")
        families.setdefault(family_label, []).append(f"{key}: {description}")

    # Evita explode: no máximo 8 sensores lógicos por boia a partir de parâmetros.
    for family_label, lines in list(families.items())[:8]:
        sensor_type, _ = _infer_sensor_type(family_label)
        serial = f"PNBOIA-{buoy_id}-{_slug(family_label)}"
        sensors.append(
            {
                "sensor_type": sensor_type,
                "family": family_label[:120],
                "brand": brand,
                "model": model,
                "serial_number": serial[:160],
                "operational_status": status,
                "notes": f"{SENSOR_MARKER_PREFIX}{buoy_id}:{_slug(family_label)}\nParâmetros associados:\n"
                + "\n".join(lines[:12]),
                "installation_notes": f"Sensor lógico derivado dos parâmetros da boia {buoy_id}.",
                "marker": f"{SENSOR_MARKER_PREFIX}{buoy_id}:{_slug(family_label)}",
            }
        )
    return sensors


def buoy_to_enriched_payload(buoy: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = metadata or {}
    boia = meta.get("boia") if isinstance(meta.get("boia"), dict) else {}
    buoy_type = str(buoy.get("type") or "BOIA").strip() or "BOIA"
    manufacturer = _clean(boia.get("fabricante")) or buoy_type
    model = _clean(boia.get("modelo")) or buoy_type
    name = str(buoy.get("name") or meta.get("nome") or f"Boia {buoy['buoy_id']}").strip()
    mode = str(buoy.get("mode") or meta.get("situacao") or "")
    return {
        "source_key": f"pnboia-buoy:{buoy['buoy_id']}",
        "external_id": int(buoy["buoy_id"]),
        "name": name[:180],
        "platform_type": buoy_type.lower(),
        "manufacturer": manufacturer[:160] if manufacturer else None,
        "model": model[:160] if model else None,
        "operational_status": map_operational_status(is_active=bool(buoy.get("is_active")), mode=mode),
        "description": build_description(buoy, meta),
        "is_active": bool(buoy.get("is_active")),
        "mode": mode,
        "latitude": buoy.get("latitude"),
        "longitude": buoy.get("longitude"),
        "local": buoy.get("local"),
        "hull": build_hull_payload(buoy, meta),
        "systems": build_systems_payload(buoy, meta),
        "sensors": build_sensors_payload(buoy, meta),
        "metadata": meta,
    }


def buoy_to_platform_payload(buoy: dict[str, Any]) -> dict[str, Any]:
    # Compatibilidade com import antigo (sem metadata).
    return buoy_to_enriched_payload(buoy, metadata=None)


def _fetch_json(url: str, timeout: float = 30.0) -> Any:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PNBOIA HTTP {exc.code}: {body[:300]}") from exc
    return json.loads(raw)


def fetch_available_buoys(
    *,
    base_url: str = DEFAULT_PNBOIA_BASE_URL,
    token: str = DEFAULT_PNBOIA_TOKEN,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Busca todas as boias e marca ativas com base no filtro operative=true."""
    root = base_url.rstrip("/")

    def url(operative: bool | None) -> str:
        params: dict[str, str] = {"token": token, "response_type": "json"}
        if operative is not None:
            params["operative"] = "true" if operative else "false"
        return f"{root}/v1/info/available_buoys?{urllib.parse.urlencode(params)}"

    active_raw = _fetch_json(url(True), timeout=timeout)
    all_raw = _fetch_json(url(False), timeout=timeout)
    if not isinstance(active_raw, list) or not isinstance(all_raw, list):
        raise RuntimeError("Resposta inesperada da API PNBOIA available_buoys.")

    active_ids = {
        int(item["buoy_id"])
        for item in active_raw
        if isinstance(item, dict) and item.get("buoy_id") is not None
    }

    by_id: dict[int, dict[str, Any]] = {}
    for item in all_raw:
        if not isinstance(item, dict) or item.get("buoy_id") is None:
            continue
        buoy_id = int(item["buoy_id"])
        payload = dict(item)
        payload["is_active"] = buoy_id in active_ids
        by_id[buoy_id] = payload

    for item in active_raw:
        if not isinstance(item, dict) or item.get("buoy_id") is None:
            continue
        buoy_id = int(item["buoy_id"])
        payload = dict(item)
        payload["is_active"] = True
        by_id[buoy_id] = payload

    return [by_id[key] for key in sorted(by_id)]


def fetch_buoy_metadata(
    buoy_id: int,
    *,
    base_url: str = DEFAULT_PNBOIA_BASE_URL,
    token: str = DEFAULT_PNBOIA_TOKEN,
    timeout: float = 30.0,
) -> dict[str, Any]:
    root = base_url.rstrip("/")
    params = urllib.parse.urlencode(
        {"token": token, "buoy_id": str(buoy_id), "response_type": "json"}
    )
    data = _fetch_json(f"{root}/v1/info/metadata?{params}", timeout=timeout)
    if not isinstance(data, dict):
        raise RuntimeError(f"Metadados inesperados para buoy_id={buoy_id}")
    return data


def fetch_platform_payloads(
    *,
    base_url: str = DEFAULT_PNBOIA_BASE_URL,
    token: str = DEFAULT_PNBOIA_TOKEN,
    timeout: float = 30.0,
    include_metadata: bool = True,
) -> list[dict[str, Any]]:
    buoys = fetch_available_buoys(base_url=base_url, token=token, timeout=timeout)
    payloads: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for buoy in buoys:
        metadata: dict[str, Any] | None = None
        if include_metadata:
            try:
                metadata = fetch_buoy_metadata(
                    int(buoy["buoy_id"]),
                    base_url=base_url,
                    token=token,
                    timeout=timeout,
                )
            except Exception as exc:  # noqa: BLE001 - coleta e segue
                errors.append({"buoy_id": buoy.get("buoy_id"), "error": str(exc)[:200]})
                metadata = None
        payload = buoy_to_enriched_payload(buoy, metadata)
        payload["metadata_error"] = next(
            (item["error"] for item in errors if item["buoy_id"] == buoy.get("buoy_id")),
            None,
        )
        payloads.append(payload)
    return payloads
