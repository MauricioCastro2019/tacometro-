"""review v2: nuevos criterios 1-5, user opcional, campos extra

Revision ID: f1a2b3c4d5e6
Revises: d5e6f7a8b9c0
Create Date: 2026-05-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f1a2b3c4d5e6'
down_revision = 'a5ff7bff577c'
branch_labels = None
depends_on = None


def upgrade():
    # Usamos batch para compatibilidad con SQLite
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        # Eliminar constraint único (user_id, place_id)
        batch_op.drop_constraint('uq_user_place_review', type_='unique')

        # Hacer user_id nullable
        batch_op.alter_column('user_id',
                              existing_type=sa.Integer(),
                              nullable=True)

        # Agregar columnas nuevas (con server_default para filas existentes)
        batch_op.add_column(sa.Column('nickname', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('sabor', sa.Float(), nullable=False, server_default='3.0'))
        batch_op.add_column(sa.Column('salsa', sa.Float(), nullable=False, server_default='3.0'))
        batch_op.add_column(sa.Column('servicio', sa.Float(), nullable=False, server_default='3.0'))
        batch_op.add_column(sa.Column('precio_calidad', sa.Float(), nullable=False, server_default='3.0'))
        batch_op.add_column(sa.Column('higiene', sa.Float(), nullable=False, server_default='3.0'))
        batch_op.add_column(sa.Column('comentario', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('foto_comida', sa.String(512), nullable=True))
        batch_op.add_column(sa.Column('volveria', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('gasto_aproximado', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('tacos_probados', sa.String(256), nullable=True))

        # Eliminar columnas antiguas
        batch_op.drop_column('taste_score')
        batch_op.drop_column('meat_score')
        batch_op.drop_column('sauce_score')
        batch_op.drop_column('tortilla_score')
        batch_op.drop_column('value_score')
        batch_op.drop_column('hygiene_score')
        batch_op.drop_column('comment')
        batch_op.drop_column('image_url')


def downgrade():
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        # Restaurar columnas antiguas
        batch_op.add_column(sa.Column('taste_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('meat_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('sauce_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('tortilla_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('value_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('hygiene_score', sa.Float(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.String(256), nullable=True))

        # Eliminar columnas nuevas
        batch_op.drop_column('nickname')
        batch_op.drop_column('sabor')
        batch_op.drop_column('salsa')
        batch_op.drop_column('servicio')
        batch_op.drop_column('precio_calidad')
        batch_op.drop_column('higiene')
        batch_op.drop_column('comentario')
        batch_op.drop_column('foto_comida')
        batch_op.drop_column('volveria')
        batch_op.drop_column('gasto_aproximado')
        batch_op.drop_column('tacos_probados')

        # Restaurar user_id como NOT NULL
        batch_op.alter_column('user_id',
                              existing_type=sa.Integer(),
                              nullable=False)

        # Restaurar constraint único
        batch_op.create_unique_constraint('uq_user_place_review', ['user_id', 'place_id'])
