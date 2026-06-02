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
    """Carga datos iniciales: categorías y taquerías de ejemplo."""
    click.echo('Creando categorías...')
    for name, icon in TACO_CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, slug=slugify(name), icon=icon)
            db.session.add(cat)
    db.session.commit()
    click.echo(f'{len(TACO_CATEGORIES)} tipos de taco listos.')

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


@current_app.cli.command('create-admin')
@click.option('--username', prompt='Nombre de usuario', help='Username del nuevo admin')
@click.option('--phone', prompt='Teléfono (10 dígitos)', help='Teléfono del nuevo admin')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
              help='Contraseña del nuevo admin')
def create_admin(username, phone, password):
    """Crea un usuario administrador o promueve uno existente."""
    existing_phone = User.query.filter_by(phone=phone).first()
    existing_username = User.query.filter_by(username=username).first()

    if existing_phone and existing_phone.username != username:
        click.echo(f'Error: el teléfono {phone} ya está registrado con otro usuario.', err=True)
        return

    if existing_username and existing_username.phone != phone:
        click.echo(f'Error: el usuario "{username}" ya existe con otro teléfono.', err=True)
        return

    user = existing_phone or existing_username
    if user:
        if user.is_admin:
            click.echo(f'"{username}" ya es administrador.')
        else:
            user.role = 'admin'
            db.session.commit()
            click.echo(f'Usuario "{username}" promovido a administrador.')
    else:
        user = User(username=username, phone=phone, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin creado: {username} / {phone}')


@current_app.cli.command('set-role')
@click.argument('username')
@click.argument('role', type=click.Choice(['user', 'admin', 'owner']))
def set_role(username, role):
    """Asigna un rol a un usuario existente. Uso: flask set-role <username> <role>"""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'Usuario "{username}" no encontrado.', err=True)
        return
    old_role = user.role
    user.role = role
    db.session.commit()
    click.echo(f'"{username}": {old_role} → {role}')
