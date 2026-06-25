from alembic import op
import sqlalchemy as sa


revision = '0006_event_mount_rules_and_checkin_snapshot'
down_revision = '0005_add_event_build_slots'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('zvz_events', sa.Column('mount_gallop_requirement', sa.Integer(), nullable=False, server_default='120'))
    op.add_column('zvz_events', sa.Column('mount_requirement_note', sa.Text(), nullable=True))
    op.add_column('checkins', sa.Column('player_nick_snapshot', sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column('checkins', 'player_nick_snapshot')
    op.drop_column('zvz_events', 'mount_requirement_note')
    op.drop_column('zvz_events', 'mount_gallop_requirement')
