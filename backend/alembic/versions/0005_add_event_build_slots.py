from alembic import op
import sqlalchemy as sa


revision = '0005_add_event_build_slots'
down_revision = '0004_add_build_slot_item_images'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('event_builds', sa.Column('max_slots', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('event_builds', 'max_slots')
