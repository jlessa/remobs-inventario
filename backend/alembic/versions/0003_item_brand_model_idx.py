"""Índices em brand e model para autocomplete rápido.

Revision ID: 0003_item_brand_model_idx
Revises: 0002_add_field_checklists
Create Date: 2026-08-06
"""

from __future__ import annotations

from alembic import op


revision = "0003_item_brand_model_idx"
down_revision = "0002_add_field_checklists"
branch_labels = None
depends_on = None

SCHEMA: str | None = None


def upgrade() -> None:
    op.create_index(
        "ix_inventory_items_brand",
        "inventory_items",
        ["brand"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_inventory_items_model",
        "inventory_items",
        ["model"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_items_model", table_name="inventory_items", schema=SCHEMA)
    op.drop_index("ix_inventory_items_brand", table_name="inventory_items", schema=SCHEMA)
