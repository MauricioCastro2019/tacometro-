import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import current_user, login_required
from app.owner import owner
from app.models.place import Place
from app.models.claim import PlaceClaim
from app.models.category import Category
from app.extensions import db
from app.admin.forms import PlaceForm
from app.utils.image_upload import upload_image
from app.utils.slugify import slugify

_DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']


def _category_choices():
    return [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


def _parse_horario_form():
    horario = {}
    for dia in _DIAS:
        if request.form.get(f'dia_{dia}'):
            abre = request.form.get(f'abre_{dia}', '').strip()
            cierra = request.form.get(f'cierra_{dia}', '').strip()
            if abre and cierra:
                horario[dia] = {'abre': abre, 'cierra': cierra}
    return json.dumps(horario) if horario else None


def _require_owner_or_admin(place):
    if place.owner_id != current_user.id and not current_user.is_admin:
        abort(403)


@owner.route('/')
@login_required
def index():
    places = current_user.owned_places
    if len(places) == 1:
        return redirect(url_for('owner.dashboard', slug=places[0].slug))
    return render_template('owner/mis_taquerias.html', places=places)


@owner.route('/<slug>')
@login_required
def dashboard(slug):
    place = Place.query.filter_by(slug=slug).first_or_404()
    _require_owner_or_admin(place)

    from app.models.review import Review

    all_reviews = (
        Review.query
        .filter_by(place_id=place.id, is_visible=True)
        .order_by(Review.created_at.desc())
        .all()
    )

    total = len(all_reviews)
    avg = round(sum(r.overall_score for r in all_reviews) / total, 1) if total else None
    volveria_count = sum(1 for r in all_reviews if r.volveria is True)
    pct_volveria = round(volveria_count / total * 100) if total else None
    gastos = [r.gasto_aproximado for r in all_reviews if r.gasto_aproximado and r.gasto_aproximado > 0]
    gasto_prom = round(sum(gastos) / len(gastos)) if gastos else None

    criterios = None
    if all_reviews:
        n = total
        criterios = {
            'Sabor': round(sum(r.sabor for r in all_reviews) / n, 1),
            'Salsa': round(sum(r.salsa for r in all_reviews) / n, 1),
            'Servicio': round(sum(r.servicio for r in all_reviews) / n, 1),
            'Precio/cal.': round(sum(r.precio_calidad for r in all_reviews) / n, 1),
            'Higiene': round(sum(r.higiene for r in all_reviews) / n, 1),
        }

    # Tendencia últimas 8 semanas
    now = datetime.now(timezone.utc)
    week_buckets = defaultdict(list)
    for r in all_reviews:
        d = r.created_at
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        monday = (d - timedelta(days=d.weekday())).date()
        week_buckets[monday.isoformat()].append(r.overall_score)

    trend = []
    for i in range(7, -1, -1):
        day = (now - timedelta(weeks=i)).date()
        monday = day - timedelta(days=day.weekday())
        key = monday.isoformat()
        scores = week_buckets.get(key, [])
        trend.append({
            'label': monday.strftime('%d/%m'),
            'avg': round(sum(scores) / len(scores), 1) if scores else None,
            'count': len(scores),
        })

    return render_template('owner/dashboard.html',
                           place=place,
                           total=total,
                           avg=avg,
                           pct_volveria=pct_volveria,
                           gasto_prom=gasto_prom,
                           criterios=criterios,
                           trend=trend,
                           recent_reviews=all_reviews[:5])


@owner.route('/<slug>/editar', methods=['GET', 'POST'])
@login_required
def edit(slug):
    place = Place.query.filter_by(slug=slug).first_or_404()
    _require_owner_or_admin(place)

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
            place.horario = _parse_horario_form()
            place.categories = Category.query.filter(
                Category.id.in_(form.category_ids.data)
            ).all()
            db.session.commit()
            flash('¡Información actualizada correctamente!', 'success')
            return redirect(url_for('owner.dashboard', slug=place.slug))

    horario_parsed = {}
    if place.horario:
        try:
            horario_parsed = json.loads(place.horario)
        except (ValueError, TypeError):
            pass

    return render_template('owner/edit.html', form=form, place=place,
                           horario_parsed=horario_parsed)


@owner.route('/reclamar/<int:place_id>', methods=['POST'])
@login_required
def reclamar(place_id):
    place = db.session.get(Place, place_id) or abort(404)

    if place.owner_id is not None:
        flash('Esta taquería ya tiene un dueño verificado.', 'warning')
        return redirect(url_for('places.detail', slug=place.slug))

    existing = PlaceClaim.query.filter_by(
        place_id=place.id,
        user_id=current_user.id,
        status='pending',
    ).first()
    if existing:
        flash('Ya tienes una solicitud pendiente para esta taquería.', 'info')
        return redirect(url_for('places.detail', slug=place.slug))

    claim = PlaceClaim(
        place_id=place.id,
        user_id=current_user.id,
        status='pending',
        message=request.form.get('message', '').strip() or None,
    )
    db.session.add(claim)
    db.session.commit()
    flash('¡Solicitud enviada! El equipo de Tacómetro la revisará pronto.', 'success')
    return redirect(url_for('places.detail', slug=place.slug))
