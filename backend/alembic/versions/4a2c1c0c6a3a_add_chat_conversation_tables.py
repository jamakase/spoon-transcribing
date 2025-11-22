from alembic import op
import sqlalchemy as sa


revision = "4a2c1c0c6a3a"
down_revision = "8f2b6a1f2b1c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name="fk_chat_messages_conversation_id_conversations"),
    )
    op.create_index(
        "ix_chat_messages_conversation_id_created_at",
        "chat_messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_chat_messages_conversation_id_created_at", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_table("conversations")