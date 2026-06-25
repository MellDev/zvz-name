from alembic import op
import sqlalchemy as sa


revision = '0009_add_event_discord_message_extra'
down_revision = '0008_add_build_skills'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('zvz_events', sa.Column('discord_message_extra', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('zvz_events', 'discord_message_extra')
