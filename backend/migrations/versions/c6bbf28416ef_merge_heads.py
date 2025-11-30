"""merge heads

Revision ID: c6bbf28416ef
Revises: aaaf1b13c34b, add_rarity_frames
Create Date: 2025-11-19 09:21:00.497272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6bbf28416ef'
down_revision: Union[str, Sequence[str], None] = ('aaaf1b13c34b', 'add_rarity_frames')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
