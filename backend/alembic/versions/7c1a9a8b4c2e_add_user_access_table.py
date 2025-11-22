from alembic import op
import sqlalchemy as sa


revision = "7c1a9a8b4c2e"
down_revision = "4a2c1c0c6a3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_access",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pubkey", sa.String(length=255), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], name="fk_user_access_meeting_id_meetings"),
    )
    op.create_index("ix_user_access_pubkey", "user_access", ["pubkey"])
    op.create_index("ix_user_access_meeting", "user_access", ["meeting_id"])


def downgrade() -> None:
    op.drop_index("ix_user_access_meeting", table_name="user_access")
    op.drop_index("ix_user_access_pubkey", table_name="user_access")
    op.drop_table("user_access")