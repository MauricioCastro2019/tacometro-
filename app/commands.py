import click
from flask import current_app
from app.extensions import db
from app.models.category import Category
from app.models.place import Place
from app.models.user import User
from app.utils.slugify import slugify


@current_app.cli.command('seed')
def seed():
    """Carga datos iniciales: categoría tacos, admin y taquerías de ejemplo."""

    # Categoría
    if not Category.query.filter_by(slug='tacos').first():
        cat = Category(name='Tacos', slug='tacos', icon='🌮')
        db.session.add(cat)
        db.session.commit()
        click.echo('Categoría "Tacos" creada.')
    else:
        cat = Category.query.filter_by(slug='tacos').first()
        click.echo('Categoría "Tacos" ya existe.')

    # Usuario admin
    if not User.query.filter_by(email='admin@tacometro.mx').first():
        admin = User(username='admin', email='admin@tacometro.mx', is_admin=True)
        admin.set_password('admin1234')
        db.session.add(admin)
        db.session.commit()
        click.echo('Admin creado: admin@tacometro.mx / admin1234')
    else:
        click.echo('Admin ya existe.')

    # Taquerías de ejemplo
    taquerias = [
        {
            'name': 'El Güero Tacos',
            'description': 'Los mejores tacos de canasta de León desde 1985. Tortilla hecha a mano, carne de primera.',
            'address': 'Blvd. López Mateos 1234, León, Gto.',
        },
        {
            'name': 'Tacos La Parroquia',
            'description': 'Especialidad en tacos al pastor y de suadero. Salsa roja que no falla.',
            'address': 'Calzada de los Héroes 567, León, Gto.',
        },
        {
            'name': 'Taquería Don Beto',
            'description': 'Tradición familiar de más de 30 años. Tacos de barbacoa los fines de semana.',
            'address': 'Mercado Hidalgo, Local 45, León, Gto.',
        },
    ]

    for t in taquerias:
        slug = slugify(t['name'])
        if not Place.query.filter_by(slug=slug).first():
            place = Place(
                name=t['name'],
                slug=slug,
                description=t['description'],
                address=t['address'],
                category_id=cat.id,
            )
            db.session.add(place)
            click.echo(f'Taquería creada: {t["name"]}')
        else:
            click.echo(f'Taquería ya existe: {t["name"]}')

    db.session.commit()
    click.echo('Seed completado.')
