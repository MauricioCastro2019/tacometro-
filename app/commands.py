import click
from flask import current_app
from app.extensions import db
from app.models.category import Category
from app.models.place import Place
from app.models.user import User
from app.utils.slugify import slugify


TACO_CATEGORIES = [
    ('Al Pastor',     '🔪'),
    ('Suadero',       '🥩'),
    ('Bistec',        '🥩'),
    ('Carnitas',      '🐷'),
    ('Barbacoa',      '🐑'),
    ('Birria',        '🍲'),
    ('Cabeza',        '🐮'),
    ('Lengua',        '🐮'),
    ('Tripa',         '🌀'),
    ('Buche',         '🐷'),
    ('Nana',          '🐮'),
    ('Costilla',      '🍖'),
    ('Chorizo',       '🌶️'),
    ('Chicharrón',    '🧀'),
    ('Pollo',         '🐓'),
    ('Cecina',        '🥓'),
    ('Machaca',       '🥩'),
    ('Canasta',       '🧺'),
    ('Pescado',       '🐟'),
    ('Camarón',       '🦐'),
    ('Cochinita',     '🐷'),
    ('Guisado',       '🍳'),
    ('Adobada',       '🌶️'),
    ('Mixto',         '🌮'),
]


@current_app.cli.command('seed-categories')
def seed_categories():
    """Crea o actualiza todos los tipos de taco."""
    created = 0
    for name, icon in TACO_CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, slug=slugify(name), icon=icon)
            db.session.add(cat)
            created += 1
            click.echo(f'  + {name}')
    db.session.commit()
    click.echo(f'{created} categorías creadas.')


@current_app.cli.command('seed')
def seed():
    """Carga datos iniciales: categorías, admin y taquerías de ejemplo."""

    # Categorías
    click.echo('Creando categorías...')
    for name, icon in TACO_CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, slug=slugify(name), icon=icon)
            db.session.add(cat)
    db.session.commit()
    click.echo(f'{len(TACO_CATEGORIES)} tipos de taco listos.')

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
    pastor = Category.query.filter_by(slug='al-pastor').first()
    suadero = Category.query.filter_by(slug='suadero').first()
    barbacoa = Category.query.filter_by(slug='barbacoa').first()
    bistec = Category.query.filter_by(slug='bistec').first()

    taquerias = [
        {
            'name': 'El Güero Tacos',
            'description': 'Los mejores tacos de canasta de León desde 1985. Tortilla hecha a mano, carne de primera.',
            'address': 'Blvd. López Mateos 1234, León, Gto.',
            'cats': [suadero, bistec],
        },
        {
            'name': 'Tacos La Parroquia',
            'description': 'Especialidad en tacos al pastor y de suadero. Salsa roja que no falla.',
            'address': 'Calzada de los Héroes 567, León, Gto.',
            'cats': [pastor, suadero],
        },
        {
            'name': 'Taquería Don Beto',
            'description': 'Tradición familiar de más de 30 años. Tacos de barbacoa los fines de semana.',
            'address': 'Mercado Hidalgo, Local 45, León, Gto.',
            'cats': [barbacoa],
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
            )
            place.categories = [c for c in t['cats'] if c]
            db.session.add(place)
            click.echo(f'Taquería creada: {t["name"]}')
        else:
            click.echo(f'Taquería ya existe: {t["name"]}')

    db.session.commit()
    click.echo('Seed completado.')
