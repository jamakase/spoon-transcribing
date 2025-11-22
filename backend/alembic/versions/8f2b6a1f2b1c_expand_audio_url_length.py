"""Expand audio_url length in meetings

Revision ID: 8f2b6a1f2b1c
Revises: 3de79ba93d50
Create Date: 2025-11-22 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f2b6a1f2b1c'
down_revision: Union[str, Sequence[str], None] = '3de79ba93d50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('meetings', 'audio_url', type_=sa.Text(), existing_type=sa.String(length=500))


def downgrade() -> None:
    op.alter_column('meetings', 'audio_url', type_=sa.String(length=500), existing_type=sa.Text())