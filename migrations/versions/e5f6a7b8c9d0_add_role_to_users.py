"""Add role column to users, remove is_admin boolean

Revision ID: e5f6a7b8c9d0
Revises: d3e4f5a6b7c8
Create Date: 2026-05-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f6a7b8c9d0'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columna role con default 'user' (nullable para la migración de datos)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(20), nullable=True))

    # Backfill: promover admins existentes, asignar 'user' al resto
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = TRUE OR is_admin = 1")
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")

    # Hacer NOT NULL y eliminar is_admin
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role', nullable=False)
        batch_op.drop_column('is_admin')


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))

    op.execute("UPDATE users SET is_admin = (role = 'admin')")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_admin', nullable=False)
        batch_op.drop_column('role')
