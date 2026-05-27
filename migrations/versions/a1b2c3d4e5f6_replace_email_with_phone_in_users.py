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
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Agregar columna phone si no existe (en SQLite ya existe por migraciones previas fallidas)
    inspector = sa.inspect(bind)
    existing_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'phone' not in existing_cols:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('phone', sa.String(10), nullable=True))

    # Asignar teléfono placeholder único por usuario (cross-db)
    if dialect == 'postgresql':
        op.execute("UPDATE users SET phone = lpad(id::text, 10, '0') WHERE phone IS NULL OR phone = ''")
    else:
        op.execute("UPDATE users SET phone = printf('%010d', id) WHERE phone IS NULL OR phone = ''")

    # Eliminar email e índice; hacer phone NOT NULL + unique
    with op.batch_alter_table('users', schema=None) as batch_op:
        existing_indexes = [i['name'] for i in inspector.get_indexes('users')]
        if 'ix_users_email' in existing_indexes:
            batch_op.drop_index('ix_users_email')
        batch_op.drop_column('email')
        batch_op.alter_column('phone',
                              existing_type=sa.String(10),
                              nullable=False)
        batch_op.create_index('ix_users_phone', ['phone'], unique=True)
        batch_op.create_unique_constraint('uq_users_phone', ['phone'])


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_phone')
        batch_op.drop_constraint('uq_users_phone', type_='unique')
        batch_op.alter_column('phone',
                              existing_type=sa.String(10),
                              nullable=True)
        batch_op.add_column(sa.Column('email', sa.String(120), nullable=True))

    if dialect == 'postgresql':
        op.execute("UPDATE users SET email = phone || '@placeholder.com' WHERE email IS NULL")
    else:
        op.execute("UPDATE users SET email = phone || '@placeholder.com' WHERE email IS NULL")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(120), nullable=False)
        batch_op.create_index('ix_users_email', ['email'], unique=True)
        batch_op.drop_column('phone')
