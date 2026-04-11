"""many-to-many categories, expand image_url

Revision ID: d5e6f7a8b9c0
Revises: b3c4d5e6f7a8
Create Date: 2026-04-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd5e6f7a8b9c0'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Crear tabla de asociación place_categories
    op.create_table(
        'place_categories',
        sa.Column('place_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('place_id', 'category_id')
    )

    # 2. Migrar datos existentes: copiar category_id de cada place a la join table
    op.execute("""
        INSERT INTO place_categories (place_id, category_id)
        SELECT id, category_id FROM places WHERE category_id IS NOT NULL
    """)

    # 3. Eliminar el FK y la columna category_id de places
    op.drop_constraint('places_category_id_fkey', 'places', type_='foreignkey')
    op.drop_column('places', 'category_id')

    # 4. Expandir image_url de 256 a 512 chars (para URLs de Cloudinary)
    op.alter_column('places', 'image_url',
                    existing_type=sa.String(length=256),
                    type_=sa.String(length=512),
                    existing_nullable=True)


def downgrade():
    # Restaurar columna category_id
    op.add_column('places', sa.Column('category_id', sa.Integer(), nullable=True))

    # Recuperar la primera categoría de la join table para cada place
    op.execute("""
        UPDATE places SET category_id = (
            SELECT category_id FROM place_categories
            WHERE place_id = places.id
            ORDER BY category_id
            LIMIT 1
        )
    """)

    # Restaurar FK
    op.create_foreign_key(
        'places_category_id_fkey', 'places', 'categories',
        ['category_id'], ['id']
    )

    op.drop_table('place_categories')

    op.alter_column('places', 'image_url',
                    existing_type=sa.String(length=512),
                    type_=sa.String(length=256),
                    existing_nullable=True)
