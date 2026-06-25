from alembic import op
import sqlalchemy as sa


revision = '0008_add_build_skills'
down_revision = '0007_event_callers_and_approval_callers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('builds', sa.Column('weapon_skills', sa.String(length=250), nullable=True))
    op.add_column('builds', sa.Column('helmet_skills', sa.String(length=250), nullable=True))
    op.add_column('builds', sa.Column('chest_skills', sa.String(length=250), nullable=True))
    op.add_column('builds', sa.Column('boots_skills', sa.String(length=250), nullable=True))


def downgrade() -> None:
    op.drop_column('builds', 'boots_skills')
    op.drop_column('builds', 'chest_skills')
    op.drop_column('builds', 'helmet_skills')
    op.drop_column('builds', 'weapon_skills')
