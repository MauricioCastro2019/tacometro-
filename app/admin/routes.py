import csv
import io
import time
import urllib.request
import urllib.parse
import json
from flask import render_template, redirect, url_for, flash, abort, request, jsonify
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


@admin.route('/places/<int:place_id>/delete', methods=['POST'])
@login_required
@admin_required
def place_delete(place_id):
    place = db.session.get(Place, place_id) or abort(404)
    name = place.name
    db.session.delete(place)
    db.session.commit()
    flash(f'Taquería "{name}" eliminada.', 'success')
    return redirect(url_for('admin.index'))


@admin.route('/reviews')
@login_required
@admin_required
def reviews_index():
    from app.models.review import Review
    reviews = (
        Review.query
        .order_by(Review.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template('admin/reviews.html', reviews=reviews)


@admin.route('/reviews/<int:review_id>/toggle', methods=['POST'])
@login_required
@admin_required
def review_toggle(review_id):
    from app.models.review import Review
    review = db.session.get(Review, review_id) or abort(404)
    review.is_visible = not review.is_visible
    db.session.commit()
    flash(f'Reseña {"visible" if review.is_visible else "oculta"}.', 'success')
    return redirect(url_for('admin.reviews_index'))


@admin.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def review_delete(review_id):
    from app.models.review import Review
    review = db.session.get(Review, review_id) or abort(404)
    db.session.delete(review)
    db.session.commit()
    flash('Reseña eliminada.', 'success')
    return redirect(url_for('admin.reviews_index'))


@admin.route('/categories')
@login_required
@admin_required
def categories_index():
    cats = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=cats)


@admin.route('/categories/new', methods=['POST'])
@login_required
@admin_required
def category_create():
    name = request.form.get('name', '').strip()
    if not name:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.categories_index'))
    if Category.query.filter_by(name=name).first():
        flash('Ya existe esa categoría.', 'warning')
        return redirect(url_for('admin.categories_index'))
    cat = Category(name=name, slug=slugify(name),
                   icon=request.form.get('icon', '').strip() or None)
    db.session.add(cat)
    db.session.commit()
    flash(f'Categoría "{name}" creada.', 'success')
    return redirect(url_for('admin.categories_index'))


@admin.route('/categories/<int:cat_id>/edit', methods=['POST'])
@login_required
@admin_required
def category_edit(cat_id):
    cat = db.session.get(Category, cat_id) or abort(404)
    name = request.form.get('name', '').strip()
    if not name:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.categories_index'))
    conflict = Category.query.filter_by(name=name).first()
    if conflict and conflict.id != cat.id:
        flash('Ya existe esa categoría.', 'warning')
        return redirect(url_for('admin.categories_index'))
    cat.name = name
    cat.slug = slugify(name)
    cat.icon = request.form.get('icon', '').strip() or None
    db.session.commit()
    flash(f'Categoría "{name}" actualizada.', 'success')
    return redirect(url_for('admin.categories_index'))


@admin.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def category_delete(cat_id):
    cat = db.session.get(Category, cat_id) or abort(404)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'Categoría "{name}" eliminada.', 'success')
    return redirect(url_for('admin.categories_index'))


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


_geocode_status = {}  # task_id → dict


@admin.route('/geocode', methods=['POST'])
@login_required
@admin_required
def geocode_places():
    import threading

    pending = Place.query.filter(
        Place.is_active == True,
        (Place.latitude == None) | (Place.longitude == None)
    ).all()

    if not pending:
        flash('Todas las taquerías ya tienen coordenadas.', 'info')
        return redirect(url_for('admin.index'))

    task_id = str(int(time.time()))
    _geocode_status[task_id] = {'done': False, 'ok': 0, 'failed': 0, 'total': len(pending)}
    place_ids = [p.id for p in pending]

    def _run(app, ids, tid):
        with app.app_context():
            status = _geocode_status[tid]
            for pid in ids:
                p = db.session.get(Place, pid)
                if not p:
                    continue
                q = f"{p.address or p.name}, León, Guanajuato, México"
                params = urllib.parse.urlencode({'q': q, 'format': 'json', 'limit': '1'})
                url = f'https://nominatim.openstreetmap.org/search?{params}'
                req = urllib.request.Request(url, headers={'User-Agent': 'Tacometro/1.0'})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read())
                    if data:
                        p.latitude  = float(data[0]['lat'])
                        p.longitude = float(data[0]['lon'])
                        db.session.commit()
                        status['ok'] += 1
                    else:
                        status['failed'] += 1
                except Exception:
                    status['failed'] += 1
                time.sleep(1.1)
            status['done'] = True

    from flask import current_app
    t = threading.Thread(target=_run, args=(current_app._get_current_object(), place_ids, task_id),
                         daemon=True)
    t.start()

    flash(f'Geocodificando {len(pending)} taquerías en segundo plano. '
          f'Puedes seguir el progreso con el botón "Estado".', 'info')
    return redirect(url_for('admin.geocode_status_page', task_id=task_id))


@admin.route('/geocode/status/<task_id>')
@login_required
@admin_required
def geocode_status_page(task_id):
    status = _geocode_status.get(task_id)
    if not status:
        flash('Tarea no encontrada.', 'warning')
        return redirect(url_for('admin.index'))
    return render_template('admin/geocode_status.html', status=status, task_id=task_id)


@admin.route('/suggestions')
@login_required
@admin_required
def suggestions_index():
    from app.models.suggestion import Suggestion
    pending  = Suggestion.query.filter_by(status='pending').order_by(Suggestion.created_at.desc()).all()
    resolved = Suggestion.query.filter(Suggestion.status != 'pending').order_by(Suggestion.created_at.desc()).limit(30).all()
    return render_template('admin/suggestions.html', pending=pending, resolved=resolved)


@admin.route('/suggestions/<int:sug_id>/approve', methods=['POST'])
@login_required
@admin_required
def suggestion_approve(sug_id):
    from app.models.suggestion import Suggestion
    sug = db.session.get(Suggestion, sug_id) or abort(404)
    sug.status = 'approved'
    # Pre-crear la taquería en borrador (inactiva para que el admin la complete)
    existing = Place.query.filter_by(slug=slugify(sug.name)).first()
    if not existing:
        place = Place(name=sug.name, slug=slugify(sug.name),
                      address=sug.address, city='León', state='Guanajuato', is_active=False)
        db.session.add(place)
        db.session.commit()
        flash(f'Sugerencia aprobada. Taquería "{sug.name}" creada en borrador — complétala antes de publicar.', 'success')
        return redirect(url_for('admin.place_edit', place_id=place.id))
    db.session.commit()
    flash('Sugerencia aprobada (la taquería ya existía).', 'info')
    return redirect(url_for('admin.suggestions_index'))


@admin.route('/suggestions/<int:sug_id>/reject', methods=['POST'])
@login_required
@admin_required
def suggestion_reject(sug_id):
    from app.models.suggestion import Suggestion
    sug = db.session.get(Suggestion, sug_id) or abort(404)
    sug.status = 'rejected'
    db.session.commit()
    flash('Sugerencia rechazada.', 'info')
    return redirect(url_for('admin.suggestions_index'))


@admin.route('/geocode/status/<task_id>/json')
@login_required
@admin_required
def geocode_status_json(task_id):
    status = _geocode_status.get(task_id, {})
    return jsonify(status)
