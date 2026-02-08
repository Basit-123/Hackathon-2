"""Add tool call logging table for MCP tool invocation tracking.

Revision ID: 002_add_tool_calls
Revises: 001_add_conversation_message
Create Date: 2026-01-25

This migration adds:
- ToolCall table (tracks MCP tool invocations for audit/debugging)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_add_tool_calls"
down_revision: Union[str, None] = "001_add_conversation_message"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tool_call table
    op.create_table(
        "toolcall",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("parameters", sa.String(), nullable=False),
        sa.Column("result", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["message.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    # Create index on tool_name for efficient tool query
    op.create_index(
        op.f("ix_toolcall_tool_name"),
        "toolcall",
        ["tool_name"],
        unique=False
    )


def downgrade() -> None:
    # Drop tool_call table and indexes
    op.drop_index(op.f("ix_toolcall_tool_name"), table_name="toolcall")
    op.drop_table("toolcall")
