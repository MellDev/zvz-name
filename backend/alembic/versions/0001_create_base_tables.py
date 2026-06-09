from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'guilds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False, unique=True),
        sa.Column('discord_server_id', sa.String(length=64), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False, server_default='free'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), sa.ForeignKey('guilds.id'), nullable=False),
        sa.Column('discord_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('discord_name', sa.String(length=120), nullable=False),
        sa.Column('albion_nick', sa.String(length=120), nullable=False),
        sa.Column('main_weapon_1', sa.String(length=120), nullable=True),
        sa.Column('main_weapon_2', sa.String(length=120), nullable=True),
        sa.Column('weapon_1_approved', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column('weapon_2_approved', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='player'),
        sa.Column('is_staff', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column('rating', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('participations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'weapons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('weapon_name', sa.String(length=120), nullable=False, unique=True),
        sa.Column('weapon_category', sa.String(length=80), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
    )

    op.create_table(
        'mounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mount_name', sa.String(length=120), nullable=False, unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
    )

    op.create_table(
        'zvz_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), sa.ForeignKey('guilds.id'), nullable=False),
        sa.Column('title', sa.String(length=180), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'checkins',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('zvz_events.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('weapon_selected', sa.String(length=120), nullable=False),
        sa.Column('mount_selected', sa.String(length=120), nullable=False),
        sa.Column('checkin_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'player_ratings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('player_ratings')
    op.drop_table('checkins')
    op.drop_table('zvz_events')
    op.drop_table('mounts')
    op.drop_table('weapons')
    op.drop_table('users')
    op.drop_table('guilds')
