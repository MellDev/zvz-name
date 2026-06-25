from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'builds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), sa.ForeignKey('guilds.id'), nullable=False),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('build_type', sa.String(length=80), nullable=False, server_default='CTA'),
        sa.Column('weapon_name', sa.String(length=120), nullable=False),
        sa.Column('weapon_item_id', sa.String(length=120), nullable=True),
        sa.Column('weapon_icon_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        'build_mounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('build_id', sa.Integer(), sa.ForeignKey('builds.id'), nullable=False),
        sa.Column('mount_name', sa.String(length=120), nullable=False),
    )
    op.create_table(
        'event_builds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('zvz_events.id'), nullable=False),
        sa.Column('build_id', sa.Integer(), sa.ForeignKey('builds.id'), nullable=False),
    )
    op.create_table(
        'player_build_approvals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('guild_id', sa.Integer(), sa.ForeignKey('guilds.id'), nullable=False),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('build_id', sa.Integer(), sa.ForeignKey('builds.id'), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('player_build_approvals')
    op.drop_table('event_builds')
    op.drop_table('build_mounts')
    op.drop_table('builds')
