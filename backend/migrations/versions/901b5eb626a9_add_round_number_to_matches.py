"""add_round_number_to_matches

Revision ID: 901b5eb626a9
Revises: c8a9173a8127
Create Date: 2025-11-25 12:33:39.607423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '901b5eb626a9'
down_revision: Union[str, Sequence[str], None] = 'c8a9173a8127'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
