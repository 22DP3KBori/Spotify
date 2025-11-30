from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_rarity_frames'
down_revision = 'e6a31d76a80e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'profile_frames',
        sa.Column('rarity', sa.String(length=50), nullable=True)
    )


def downgrade():
    op.drop_column('profile_frames', 'rarity')
