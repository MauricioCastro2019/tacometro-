"""replace email with phone in users

Revision ID: a1b2c3d4e5f6
Revises: f3a4b5c6d7e8
Create Date: 2026-05-27 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None


def upgrade():
    # Asignar teléfono único a usuarios existentes usando su id como placeholder
    op.execute(
        "UPDATE users SET phone = printf('%010d', id) WHERE phone IS NULL OR phone = ''"
    )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_email')
        batch_op.drop_column('email')
        batch_op.alter_column('phone',
                              existing_type=sa.String(10),
                              nullable=False)
        batch_op.create_index('ix_users_phone', ['phone'], unique=True)
        batch_op.create_unique_constraint('uq_users_phone', ['phone'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_phone')
        batch_op.drop_constraint('uq_users_phone', type_='unique')
        batch_op.alter_column('phone',
                              existing_type=sa.String(10),
                              nullable=True)
        batch_op.add_column(sa.Column('email', sa.String(120), nullable=True))

    op.execute("UPDATE users SET email = phone || '@placeholder.com' WHERE email IS NULL")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(120), nullable=False)
        batch_op.create_index('ix_users_email', ['email'], unique=True)
        batch_op.drop_column('phone')
