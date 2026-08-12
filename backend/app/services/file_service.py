from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import AuthUser
from app.models.file import EntityFile, FileMetadata
from app.services import file_storage
from app.services.audit_service import log_action


def serialize_entity_file(entity_file: EntityFile, file_meta: FileMetadata) -> dict:
    return {
        "id": entity_file.id,
        "file_id": file_meta.id,
        "entity_type": entity_file.entity_type,
        "entity_id": entity_file.entity_id,
        "file_role": entity_file.file_role,
        "notes": entity_file.notes,
        "original_name": file_meta.original_name,
        "mime_type": file_meta.mime_type,
        "size_bytes": file_meta.size_bytes,
        "uploaded_by": file_meta.uploaded_by,
        "created_at": file_meta.created_at,
        "download_path": f"/inventory/items/{entity_file.entity_id}/files/{entity_file.id}/content",
    }


async def list_entity_files(
    session: AsyncSession,
    *,
    entity_type: str,
    entity_id: str,
) -> list[dict]:
    rows = (
        await session.execute(
            select(EntityFile, FileMetadata)
            .join(FileMetadata, FileMetadata.id == EntityFile.file_id)
            .where(
                EntityFile.entity_type == entity_type,
                EntityFile.entity_id == entity_id,
                FileMetadata.deleted_at.is_(None),
            )
            .order_by(FileMetadata.created_at.desc())
        )
    ).all()
    return [serialize_entity_file(entity_file, file_meta) for entity_file, file_meta in rows]


async def get_entity_file_or_404(
    session: AsyncSession,
    *,
    entity_type: str,
    entity_id: str,
    entity_file_id: uuid.UUID,
) -> tuple[EntityFile, FileMetadata]:
    row = (
        await session.execute(
            select(EntityFile, FileMetadata)
            .join(FileMetadata, FileMetadata.id == EntityFile.file_id)
            .where(
                EntityFile.id == entity_file_id,
                EntityFile.entity_type == entity_type,
                EntityFile.entity_id == entity_id,
                FileMetadata.deleted_at.is_(None),
            )
        )
    ).first()
    if row is None:
        raise AppError("Arquivo não encontrado.", code="file_not_found", status_code=404)
    return row[0], row[1]


async def attach_upload(
    session: AsyncSession,
    *,
    actor: AuthUser,
    entity_type: str,
    entity_id: str,
    entity_label: str,
    file_role: str,
    original_name: str,
    mime_type: str,
    content: bytes,
    notes: str | None = None,
) -> dict:
    size_bytes = len(content)
    file_storage.validate_upload(file_role=file_role, mime_type=mime_type, size_bytes=size_bytes)

    normalized_mime = (mime_type or "").split(";")[0].strip().lower() or "application/octet-stream"
    storage_key = file_storage.build_storage_key(
        entity_type=entity_type,
        entity_id=entity_id,
        original_name=original_name,
    )
    file_storage.save_bytes(storage_key=storage_key, content=content, content_type=normalized_mime)

    file_meta = FileMetadata(
        original_name=file_storage.sanitize_filename(original_name),
        storage_key=storage_key,
        mime_type=normalized_mime,
        size_bytes=size_bytes,
        uploaded_by=actor.id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(file_meta)
    await session.flush()

    entity_file = EntityFile(
        file_id=file_meta.id,
        entity_type=entity_type,
        entity_id=entity_id,
        file_role=file_role.strip().lower(),
        notes=notes,
        created_at=datetime.now(timezone.utc),
    )
    session.add(entity_file)
    await session.flush()

    payload = serialize_entity_file(entity_file, file_meta)
    await log_action(
        session,
        actor=actor,
        action="file_uploaded",
        entity_type=entity_type,
        entity_id=entity_id,
        entity_label_snapshot=entity_label,
        after_data=payload,
        reason=f"Upload de {file_role}: {file_meta.original_name}",
        metadata={"file_id": str(file_meta.id), "entity_file_id": str(entity_file.id)},
    )
    return payload


async def soft_delete_entity_file(
    session: AsyncSession,
    *,
    actor: AuthUser,
    entity_type: str,
    entity_id: str,
    entity_label: str,
    entity_file_id: uuid.UUID,
    reason: str,
) -> None:
    entity_file, file_meta = await get_entity_file_or_404(
        session,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_file_id=entity_file_id,
    )
    before = serialize_entity_file(entity_file, file_meta)
    file_meta.deleted_at = datetime.now(timezone.utc)
    try:
        file_storage.delete_bytes(file_meta.storage_key)
    except AppError:
        # Metadado já marcado; ausência do binário não bloqueia remoção lógica.
        pass

    await log_action(
        session,
        actor=actor,
        action="file_deleted",
        entity_type=entity_type,
        entity_id=entity_id,
        entity_label_snapshot=entity_label,
        before_data=before,
        after_data={"deleted_at": file_meta.deleted_at.isoformat()},
        reason=reason,
        metadata={"file_id": str(file_meta.id), "entity_file_id": str(entity_file.id)},
    )
