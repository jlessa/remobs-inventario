from __future__ import annotations

import re
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.errors import AppError


SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")

IMAGE_MIME_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/heic",
        "image/heif",
    }
)

DOCUMENT_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
)

ALLOWED_MIME_TYPES = IMAGE_MIME_TYPES | DOCUMENT_MIME_TYPES

ALLOWED_FILE_ROLES = frozenset({"foto", "documento"})


def sanitize_filename(original_name: str) -> str:
    name = Path(original_name or "arquivo").name.strip() or "arquivo"
    cleaned = SAFE_FILENAME_RE.sub("_", name).strip("._")
    return cleaned[:180] or "arquivo"


def resolve_storage_root() -> Path:
    root = Path(settings.storage_local_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def build_storage_key(*, entity_type: str, entity_id: str, original_name: str) -> str:
    safe_name = sanitize_filename(original_name)
    relative = f"{entity_type}/{entity_id}/{uuid.uuid4().hex}_{safe_name}"
    if settings.storage_backend_normalized == "s3":
        return f"{settings.storage_s3_prefix_normalized}{relative}"
    return relative


def absolute_path_for_key(storage_key: str) -> Path:
    root = resolve_storage_root().resolve()
    target = (root / storage_key).resolve()
    if root not in target.parents and target != root:
        raise AppError("Caminho de armazenamento inválido.", code="invalid_storage_key", status_code=400)
    return target


def validate_upload(*, file_role: str, mime_type: str, size_bytes: int) -> None:
    role = (file_role or "").strip().lower()
    if role not in ALLOWED_FILE_ROLES:
        raise AppError(
            "Papel do arquivo inválido. Use 'foto' ou 'documento'.",
            code="invalid_file_role",
            status_code=400,
            meta={"allowed_roles": sorted(ALLOWED_FILE_ROLES)},
        )

    if size_bytes <= 0:
        raise AppError("Arquivo vazio não é permitido.", code="empty_file", status_code=400)

    if size_bytes > settings.storage_max_bytes:
        raise AppError(
            "Arquivo excede o tamanho máximo permitido.",
            code="file_too_large",
            status_code=400,
            meta={"max_bytes": settings.storage_max_bytes, "size_bytes": size_bytes},
        )

    normalized_mime = (mime_type or "").split(";")[0].strip().lower() or "application/octet-stream"
    if role == "foto" and normalized_mime not in IMAGE_MIME_TYPES:
        raise AppError(
            "Tipo de imagem não suportado.",
            code="unsupported_image_type",
            status_code=400,
            meta={"mime_type": normalized_mime, "allowed": sorted(IMAGE_MIME_TYPES)},
        )
    if role == "documento" and normalized_mime not in ALLOWED_MIME_TYPES:
        raise AppError(
            "Tipo de documento não suportado.",
            code="unsupported_document_type",
            status_code=400,
            meta={"mime_type": normalized_mime, "allowed": sorted(ALLOWED_MIME_TYPES)},
        )


@lru_cache(maxsize=1)
def _s3_client() -> Any:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:  # pragma: no cover - depende de instalação
        raise AppError(
            "Dependência boto3 ausente para storage S3.",
            code="s3_dependency_missing",
            status_code=500,
        ) from exc

    if not settings.storage_s3_bucket:
        raise AppError(
            "Bucket S3 não configurado (REMOBS_STORAGE_S3_BUCKET).",
            code="s3_bucket_not_configured",
            status_code=500,
        )

    return boto3.client(
        "s3",
        region_name=settings.storage_s3_region or "sa-east-1",
        config=Config(signature_version="s3v4"),
    )


def _save_local(*, storage_key: str, content: bytes) -> None:
    path = absolute_path_for_key(storage_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _read_local(storage_key: str) -> bytes:
    path = absolute_path_for_key(storage_key)
    if not path.is_file():
        raise AppError("Arquivo físico não encontrado no storage.", code="storage_file_missing", status_code=404)
    return path.read_bytes()


def _delete_local(storage_key: str) -> None:
    path = absolute_path_for_key(storage_key)
    if path.is_file():
        path.unlink()


def _save_s3(*, storage_key: str, content: bytes, content_type: str | None = None) -> None:
    client = _s3_client()
    extra: dict[str, str] = {}
    if content_type:
        extra["ContentType"] = content_type
    try:
        client.put_object(
            Bucket=settings.storage_s3_bucket,
            Key=storage_key,
            Body=content,
            ServerSideEncryption="AES256",
            **extra,
        )
    except Exception as exc:  # pragma: no cover - rede/credencial
        raise AppError(
            "Falha ao gravar arquivo no S3.",
            code="s3_put_failed",
            status_code=502,
            meta={"bucket": settings.storage_s3_bucket},
        ) from exc


def _read_s3(storage_key: str) -> bytes:
    from botocore.exceptions import ClientError

    client = _s3_client()
    try:
        response = client.get_object(Bucket=settings.storage_s3_bucket, Key=storage_key)
        return response["Body"].read()
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"NoSuchKey", "404", "NotFound", "NoSuchBucket"}:
            raise AppError("Arquivo físico não encontrado no storage.", code="storage_file_missing", status_code=404) from exc
        raise AppError(
            "Falha ao ler arquivo no S3.",
            code="s3_get_failed",
            status_code=502,
            meta={"bucket": settings.storage_s3_bucket, "error_code": error_code},
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise AppError(
            "Falha ao ler arquivo no S3.",
            code="s3_get_failed",
            status_code=502,
            meta={"bucket": settings.storage_s3_bucket},
        ) from exc


def _delete_s3(storage_key: str) -> None:
    client = _s3_client()
    try:
        client.delete_object(Bucket=settings.storage_s3_bucket, Key=storage_key)
    except Exception as exc:  # pragma: no cover
        raise AppError(
            "Falha ao remover arquivo no S3.",
            code="s3_delete_failed",
            status_code=502,
            meta={"bucket": settings.storage_s3_bucket},
        ) from exc


def save_bytes(*, storage_key: str, content: bytes, content_type: str | None = None) -> None:
    if settings.storage_backend_normalized == "s3":
        _save_s3(storage_key=storage_key, content=content, content_type=content_type)
        return
    _save_local(storage_key=storage_key, content=content)


def read_bytes(storage_key: str) -> bytes:
    if settings.storage_backend_normalized == "s3":
        return _read_s3(storage_key)
    return _read_local(storage_key)


def delete_bytes(storage_key: str) -> None:
    if settings.storage_backend_normalized == "s3":
        _delete_s3(storage_key)
        return
    _delete_local(storage_key)
