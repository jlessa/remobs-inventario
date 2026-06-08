from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_field_checklists"
down_revision = "0001_initial_inventory_schema"
branch_labels = None
depends_on = None

SCHEMA: str | None = None


def foreign_key(table: str, column: str = "id") -> str:
    if SCHEMA:
        return f"{SCHEMA}.{table}.{column}"
    return f"{table}.{column}"


def upgrade() -> None:
    op.create_table(
        "field_checklists",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("template_name", sa.String(length=180), nullable=False),
        sa.Column("platform_id", sa.Uuid(), nullable=True),
        sa.Column("platform_name", sa.String(length=180), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_step", sa.Integer(), nullable=False),
        sa.Column("total_steps", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("submitted_by_id", sa.Integer(), nullable=False),
        sa.Column("submitted_by_username", sa.String(length=160), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["platform_id"], [foreign_key("platforms")]),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("field_checklists", schema=SCHEMA)
