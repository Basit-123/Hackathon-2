"""Add conversation and message tables for chat system.

Revision ID: 001_add_conversation_message
Revises: None
Create Date: 2026-01-25

This migration adds:
- Conversation table (tracks chat sessions per user)
- Message table (stores chat history with user isolation)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_add_conversation_message"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    # Create index on user_id for efficient user queries
    op.create_index(
        op.f("ix_conversation_user_id"),
        "conversation",
        ["user_id"],
        unique=False
    )

    # Create message table
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversation.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    # Create indexes for efficient queries
    op.create_index(
        op.f("ix_message_user_id"),
        "message",
        ["user_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_message_role"),
        "message",
        ["role"],
        unique=False
    )


def downgrade() -> None:
    # Drop message table and indexes
    op.drop_index(op.f("ix_message_role"), table_name="message")
    op.drop_index(op.f("ix_message_user_id"), table_name="message")
    op.drop_table("message")

    # Drop conversation table and indexes
    op.drop_index(op.f("ix_conversation_user_id"), table_name="conversation")
    op.drop_table("conversation")
