"""add email verification table

Revision ID: 3461f54ceacd
Revises: e6a31d76a80e
Create Date: 2025-11-01 22:26:32.905054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3461f54ceacd'
down_revision: Union[str, Sequence[str], None] = 'e6a31d76a80e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass


from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'email_verification_codes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('new_email', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table('email_verification_codes')
