import click
from flask import current_app
from app.extensions import db
from app.models.category import Category
from app.models.place import Place
from app.models.user import User
from app.utils.slugify import slugify


TACO_CATEGORIES = [
    ('Asada',       '🔥'),
    ('Arrachera',   '🔥'),
    ('Bistec',      '🥩'),
    ('Pastor',      '🌮'),
    ('Suadero',     '🥩'),
    ('Tripa',       '🌀'),
    ('Costilla',    '🍖'),
    ('Chorizo',     '🌶️'),
    ('Cabeza',      '🐮'),
    ('Lengua',      '🐮'),
    ('Hígado',      '🐮'),
    ('Barbacoa',    '🐑'),
    ('Birria',      '🍲'),
    ('Carnitas',    '🐷'),
    ('Campechano',  '🌮'),
    ('Canasta',     '🧺'),
    ('Guisado',     '🍳'),
    ('Cecina',      '🥓'),
    ('Buche',       '🐷'),
    ('Chicharrón',  '🐷'),
    ('Cochinita',   '🐷'),
    ('Pescado',     '🐟'),
    ('Camarón',     '🦐'),
    ('Adobada',     '🌶️'),
    ('Machaca',     '🥩'),
    ('Mixto',       '🌮'),
    ('Vegetariano', '🌱'),
]

_CANONICAL_NAMES = {name for name, _ in TACO_CATEGORIES}


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


@current_app.cli.command('reset-categories')
def reset_categories():
    """Limpia categorías combinadas (X / Y) y sincroniza con la lista oficial."""
    # 1. Renombrar 'Al Pastor' -> 'Pastor' (migrar asociaciones)
    al_pastor = Category.query.filter_by(name='Al Pastor').first()
    pastor = Category.query.filter_by(name='Pastor').first()
    if al_pastor and not pastor:
        al_pastor.name = 'Pastor'
        al_pastor.slug = 'pastor'
        click.echo('  ~ Renombrado: Al Pastor → Pastor')
    elif al_pastor and pastor:
        # Migrar asociaciones de Al Pastor a Pastor
        db.session.execute(
            db.text(
                'UPDATE place_categories SET category_id = :new_id '
                'WHERE category_id = :old_id'
            ),
            {'new_id': pastor.id, 'old_id': al_pastor.id}
        )
        db.session.delete(al_pastor)
        click.echo('  ~ Migrado: Al Pastor → Pastor (asociaciones transferidas)')

    # 2. Eliminar categorías combinadas (contienen " / ")
    combos = Category.query.filter(Category.name.like('% / %')).all()
    for cat in combos:
        db.session.execute(
            db.text('DELETE FROM place_categories WHERE category_id = :id'),
            {'id': cat.id}
        )
        db.session.delete(cat)
        click.echo(f'  - Eliminada: {cat.name}')

    # 3. Eliminar categorías obsoletas sin taquerías
    obsoletas = ['Nana', 'Pollo', 'Al Pastor', 'Variados']
    for nombre in obsoletas:
        cat = Category.query.filter_by(name=nombre).first()
        if cat:
            count = db.session.execute(
                db.text('SELECT COUNT(*) FROM place_categories WHERE category_id = :id'),
                {'id': cat.id}
            ).scalar()
            if count == 0:
                db.session.delete(cat)
                click.echo(f'  - Eliminada (sin usos): {nombre}')

    # 4. Agregar nuevas categorías faltantes
    created = 0
    for name, icon in TACO_CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, slug=slugify(name), icon=icon)
            db.session.add(cat)
            created += 1
            click.echo(f'  + Creada: {name}')

    db.session.commit()
    click.echo(f'Reset completado. {created} categorías nuevas, {len(combos)} combos eliminados.')


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

    pastor = Category.query.filter_by(slug='pastor').first()
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
