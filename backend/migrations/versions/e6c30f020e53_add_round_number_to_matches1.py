"""add_round_number_to_matches1

Revision ID: e6c30f020e53
Revises: 901b5eb626a9
Create Date: 2025-11-25 12:40:25.268257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6c30f020e53'
down_revision: Union[str, Sequence[str], None] = '901b5eb626a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
