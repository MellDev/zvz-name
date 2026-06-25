from alembic import op
import sqlalchemy as sa


revision = '0007_event_callers_and_approval_callers'
down_revision = '0006_event_mount_rules_and_checkin_snapshot'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('zvz_events', sa.Column('caller', sa.String(length=30), nullable=True))
    op.add_column('player_build_approvals', sa.Column('caller', sa.String(length=30), nullable=True))


def downgrade() -> None:
    op.drop_column('player_build_approvals', 'caller')
    op.drop_column('zvz_events', 'caller')
