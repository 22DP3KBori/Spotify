from alembic import op
import sqlalchemy as sa


revision = '6a728a77f1d5'
down_revision = 'e6c30f020e53'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('matches', sa.Column('round_number', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('matches', 'round_number')