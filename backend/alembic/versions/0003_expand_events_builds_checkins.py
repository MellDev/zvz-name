from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('zvz_events', sa.Column('content_type', sa.String(length=80), nullable=False, server_default='ZvZ'))
    op.add_column('checkins', sa.Column('build_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_checkins_build_id_builds', 'checkins', 'builds', ['build_id'], ['id'])

    op.add_column('builds', sa.Column('role', sa.String(length=50), nullable=False, server_default='DPS'))
    op.add_column('builds', sa.Column('offhand', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('helmet', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('chest', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('boots', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('cape', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('food', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('potion', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('recommended_mount', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('required_level', sa.Integer(), nullable=True))
    op.add_column('builds', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('builds', 'updated_at')
    op.drop_column('builds', 'required_level')
    op.drop_column('builds', 'recommended_mount')
    op.drop_column('builds', 'potion')
    op.drop_column('builds', 'food')
    op.drop_column('builds', 'cape')
    op.drop_column('builds', 'boots')
    op.drop_column('builds', 'chest')
    op.drop_column('builds', 'helmet')
    op.drop_column('builds', 'offhand')
    op.drop_column('builds', 'role')
    op.drop_constraint('fk_checkins_build_id_builds', 'checkins', type_='foreignkey')
    op.drop_column('checkins', 'build_id')
    op.drop_column('zvz_events', 'content_type')
