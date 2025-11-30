"""add discipline to tournaments

Revision ID: c279fea5bb67
Revises: fd874ace1bd1
Create Date: 2025-11-24 13:22:51.894716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c279fea5bb67'
down_revision: Union[str, Sequence[str], None] = 'fd874ace1bd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('tournaments', sa.Column('discipline', sa.String(50), nullable=False, server_default='Unknown'))

def downgrade():
    op.drop_column('tournaments', 'discipline')
