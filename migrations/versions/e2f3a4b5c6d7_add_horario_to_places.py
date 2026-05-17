"""add horario to places

Revision ID: e2f3a4b5c6d7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e2f3a4b5c6d7'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('places', schema=None) as batch_op:
        batch_op.add_column(sa.Column('horario', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('places', schema=None) as batch_op:
        batch_op.drop_column('horario')
