"""add salsas_probadas, bebidas, postres to reviews

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-05-16 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f3a4b5c6d7e8'
down_revision = 'e2f3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('salsas_probadas', sa.String(256), nullable=True))
        batch_op.add_column(sa.Column('bebidas', sa.String(128), nullable=True))
        batch_op.add_column(sa.Column('postres', sa.String(128), nullable=True))


def downgrade():
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_column('postres')
        batch_op.drop_column('bebidas')
        batch_op.drop_column('salsas_probadas')
