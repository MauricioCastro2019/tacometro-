import csv
import io
import time
import urllib.request
import urllib.parse
import json
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.admin import admin
from app.admin.forms import PlaceForm, ImportForm
from app.extensions import db
from app.models.category import Category
from app.models.place import Place
from app.utils.decorators import admin_required
from app.utils.image_upload import upload_image
from app.utils.slugify import slugify


def _category_choices():
    return [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


@admin.route('/')
@login_required
@admin_required
def index():
    places = Place.query.order_by(Place.name).all()
    return render_template('admin/index.html', places=places)


@admin.route('/places/new', methods=['GET', 'POST'])
@login_required
@admin_required
def place_create():
    form = PlaceForm()
    form.category_ids.choices = _category_choices()

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Place.query.filter_by(slug=slug).first():
            flash('Ya existe una taquería con ese nombre.', 'danger')
        else:
            # Imagen: archivo tiene prioridad sobre URL
            image_url = form.image_url.data or None
            if form.image_file.data and form.image_file.data.filename:
                uploaded = upload_image(form.image_file.data)
                if uploaded:
                    image_url = uploaded

            place = Place(
                name=form.name.data,
                slug=slug,
                description=form.description.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_url=image_url,
                is_active=form.is_active.data,
            )
            place.categories = Category.query.filter(
                Category.id.in_(form.category_ids.data)
            ).all()
            db.session.add(place)
            db.session.commit()
            flash(f'Taquería "{place.name}" creada.', 'success')
            return redirect(url_for('admin.index'))

    return render_template('admin/place_form.html', form=form, title='Nueva taquería')


@admin.route('/places/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def place_edit(place_id):
    place = db.session.get(Place, place_id) or abort(404)
    form = PlaceForm(obj=place)
    form.category_ids.choices = _category_choices()

    if request.method == 'GET':
        form.category_ids.data = [c.id for c in place.categories]

    if form.validate_on_submit():
        new_slug = slugify(form.name.data)
        existing = Place.query.filter_by(slug=new_slug).first()
        if existing and existing.id != place.id:
            flash('Ya existe una taquería con ese nombre.', 'danger')
        else:
            # Imagen: archivo tiene prioridad sobre URL
            image_url = form.image_url.data or None
            if form.image_file.data and form.image_file.data.filename:
                uploaded = upload_image(form.image_file.data)
                if uploaded:
                    image_url = uploaded

            place.name = form.name.data
            place.slug = new_slug
            place.description = form.description.data
            place.address = form.address.data
            place.city = form.city.data
            place.state = form.state.data
            place.phone = form.phone.data
            place.image_url = image_url
            place.is_active = form.is_active.data
            place.categories = Category.query.filter(
                Category.id.in_(form.category_ids.data)
            ).all()
            db.session.commit()
            flash(f'Taquería "{place.name}" actualizada.', 'success')
            return redirect(url_for('admin.index'))

    return render_template('admin/place_form.html', form=form, title='Editar taquería', place=place)


def _normalize_header(h):
    return h.strip().lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('/', '').replace(' ', '')


def _find_header_row(rows):
    for i, row in enumerate(rows):
        normalized = [_normalize_header(str(c)) if c else '' for c in row]
        if 'nombre' in normalized:
            return i
    return 0


def _parse_rows(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith('.xlsx'):
        import openpyxl
        wb = openpyxl.load_workbook(file_storage, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        header_idx = _find_header_row(rows)
        headers = [_normalize_header(str(c)) if c else '' for c in rows[header_idx]]
        return [
            {headers[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(row)}
            for row in rows[header_idx + 1:]
        ]
    else:
        content = file_storage.read().decode('utf-8-sig')
        sample = content[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        except csv.Error:
            dialect = csv.excel
        all_rows = list(csv.reader(io.StringIO(content), dialect=dialect))
        if not all_rows:
            return []
        header_idx = _find_header_row(all_rows)
        headers = [_normalize_header(c) for c in all_rows[header_idx]]
        return [
            {headers[i]: (v.strip() if v else '') for i, v in enumerate(row)}
            for row in all_rows[header_idx + 1:]
            if any(v.strip() for v in row)
        ]


def _get_or_create_category(name):
    name = name.strip() or 'General'
    cat = Category.query.filter_by(name=name).first()
    if not cat:
        cat = Category(name=name, slug=slugify(name))
        db.session.add(cat)
        db.session.flush()
    return cat


@admin.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_places():
    form = ImportForm()
    if form.validate_on_submit():
        rows = _parse_rows(form.file.data)
        if not rows:
            flash('El archivo está vacío o no se pudo leer.', 'danger')
            return redirect(url_for('admin.import_places'))
        detected_cols = list(rows[0].keys())
        created = skipped = errors = 0
        for row in rows:
            name = row.get('nombre', '')
            if not name:
                continue
            slug = slugify(name)
            if Place.query.filter_by(slug=slug).first():
                skipped += 1
                continue
            especialidad = row.get('especialidad', '') or 'General'
            try:
                cat = _get_or_create_category(especialidad)
                direccion = row.get('direccion', '')
                zona = row.get('zonacolonia', '') or row.get('zona', '')
                horario = row.get('horario', '')
                description_parts = []
                if zona:
                    description_parts.append(f'Zona: {zona}')
                if horario:
                    description_parts.append(f'Horario: {horario}')
                place = Place(
                    name=name,
                    slug=slug,
                    description=' | '.join(description_parts) or None,
                    address=direccion or None,
                    city='León',
                    state='Guanajuato',
                    is_active=True,
                )
                place.categories = [cat]
                db.session.add(place)
                created += 1
            except Exception:
                db.session.rollback()
                errors += 1
                continue
        db.session.commit()
        msg = f'{created} taquerías importadas.'
        if skipped:
            msg += f' {skipped} omitidas (ya existían).'
        if errors:
            msg += f' {errors} con error.'
        if created == 0:
            msg += f' Columnas detectadas: {detected_cols}.'
        flash(msg, 'success' if created > 0 else 'warning')
        return redirect(url_for('admin.index'))
    return render_template('admin/import.html', form=form)


@admin.route('/geocode', methods=['POST'])
@login_required
@admin_required
def geocode_places():
    places = Place.query.filter(
        Place.is_active == True,
        (Place.latitude == None) | (Place.longitude == None)
    ).all()

    if not places:
        flash('Todas las taquerías ya tienen coordenadas.', 'info')
        return redirect(url_for('admin.index'))

    ok = failed = 0
    for place in places:
        query = f"{place.address or place.name}, León, Guanajuato, México"
        params = urllib.parse.urlencode({'q': query, 'format': 'json', 'limit': '1'})
        url = f'https://nominatim.openstreetmap.org/search?{params}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Tacometro/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            if data:
                place.latitude = float(data[0]['lat'])
                place.longitude = float(data[0]['lon'])
                ok += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        time.sleep(1.1)

    db.session.commit()
    msg = f'{ok} taquerías geocodificadas.'
    if failed:
        msg += f' {failed} sin resultado (dirección no encontrada).'
    flash(msg, 'success' if ok else 'warning')
    return redirect(url_for('admin.index'))
