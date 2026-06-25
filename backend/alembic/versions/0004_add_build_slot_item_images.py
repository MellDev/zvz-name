from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('builds', sa.Column('offhand_item_id', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('offhand_icon_url', sa.String(length=500), nullable=True))
    op.add_column('builds', sa.Column('helmet_item_id', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('helmet_icon_url', sa.String(length=500), nullable=True))
    op.add_column('builds', sa.Column('chest_item_id', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('chest_icon_url', sa.String(length=500), nullable=True))
    op.add_column('builds', sa.Column('boots_item_id', sa.String(length=120), nullable=True))
    op.add_column('builds', sa.Column('boots_icon_url', sa.String(length=500), nullable=True))


def downgrade():
    op.drop_column('builds', 'boots_icon_url')
    op.drop_column('builds', 'boots_item_id')
    op.drop_column('builds', 'chest_icon_url')
    op.drop_column('builds', 'chest_item_id')
    op.drop_column('builds', 'helmet_icon_url')
    op.drop_column('builds', 'helmet_item_id')
    op.drop_column('builds', 'offhand_icon_url')
    op.drop_column('builds', 'offhand_item_id')
