"""add coordinates to places

Revision ID: b3c4d5e6f7a8
Revises: 6b1d1a107a81
Create Date: 2026-04-08 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3c4d5e6f7a8'
down_revision = '6b1d1a107a81'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('places', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('places', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('places', 'longitude')
    op.drop_column('places', 'latitude')
