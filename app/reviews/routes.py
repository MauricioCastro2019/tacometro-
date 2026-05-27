import logging
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app.reviews import reviews
from app.reviews.forms import ReviewForm
from app.extensions import db
from app.models.place import Place
from app.models.review import Review
from app.utils.image_upload import upload_image

logger = logging.getLogger(__name__)


@reviews.route('/new', methods=['GET', 'POST'])
def create():
    place_id = request.args.get('place_id', type=int) or request.form.get('place_id', type=int)
    if not place_id:
        abort(400)

    place = db.session.get(Place, place_id) or abort(404)

    if current_user.is_authenticated:
        existing = Review.query.filter_by(user_id=current_user.id, place_id=place.id).first()
        if existing:
            flash('Ya tienes una reseña para esta taquería.', 'warning')
            return redirect(url_for('places.detail', slug=place.slug))

    form = ReviewForm()
    if request.method == 'GET':
        form.place_id.data = place.id

    if form.validate_on_submit():
        try:
            foto_url = None
            if form.foto_comida.data and form.foto_comida.data.filename:
                foto_url = upload_image(form.foto_comida.data)

            review = Review(
                user_id=current_user.id if current_user.is_authenticated else None,
                nickname=form.nickname.data.strip() if form.nickname.data else None,
                place_id=place.id,
                sabor=form.sabor.data,
                salsa=form.salsa.data,
                servicio=form.servicio.data,
                precio_calidad=form.precio_calidad.data,
                higiene=form.higiene.data,
                comentario=form.comentario.data.strip() if form.comentario.data else None,
                foto_comida=foto_url,
            )
            db.session.add(review)
            db.session.commit()
            flash('¡Reseña publicada! Gracias por tu Tacómetro.', 'success')
            return redirect(url_for('califica.confirmacion', review_id=review.id))
        except Exception:
            db.session.rollback()
            logger.exception('Error al guardar reseña')
            flash('Ocurrió un error al guardar tu reseña. Intenta de nuevo.', 'danger')

    return render_template('reviews/create.html', form=form, place=place)


@reviews.route('/<int:review_id>/edit', methods=['GET', 'POST'])
def edit(review_id):
    review = db.session.get(Review, review_id) or abort(404)

    if not current_user.is_authenticated:
        flash('Debes iniciar sesión para editar una reseña.', 'warning')
        return redirect(url_for('auth.login'))
    if review.user_id != current_user.id:
        abort(403)

    form = ReviewForm(obj=review)

    if request.method == 'GET':
        form.sabor.data = int(review.sabor)
        form.salsa.data = int(review.salsa)
        form.servicio.data = int(review.servicio)
        form.precio_calidad.data = int(review.precio_calidad)
        form.higiene.data = int(review.higiene)

    if form.validate_on_submit():
        try:
            review.sabor = form.sabor.data
            review.salsa = form.salsa.data
            review.servicio = form.servicio.data
            review.precio_calidad = form.precio_calidad.data
            review.higiene = form.higiene.data
            review.comentario = form.comentario.data.strip() if form.comentario.data else None

            if form.foto_comida.data and form.foto_comida.data.filename:
                uploaded = upload_image(form.foto_comida.data)
                if uploaded:
                    review.foto_comida = uploaded

            # Campos extra
            volveria_raw = request.form.get('volveria', '')
            review.volveria = True if volveria_raw == 'si' else (False if volveria_raw == 'no' else None)

            gasto = None
            try:
                gasto_s = request.form.get('gasto_aproximado', '').strip()
                if gasto_s:
                    gasto = float(gasto_s)
            except (ValueError, TypeError):
                pass
            review.gasto_aproximado = gasto

            tacos = request.form.get('tacos_probados', '').strip() or None
            review.tacos_probados = tacos[:256] if tacos else None

            salsas = request.form.get('salsas_probadas', '').strip() or None
            review.salsas_probadas = salsas[:256] if salsas else None

            bebidas = request.form.get('bebidas', '').strip() or None
            review.bebidas = bebidas[:128] if bebidas else None

            postres = request.form.get('postres', '').strip() or None
            review.postres = postres[:128] if postres else None

            db.session.commit()
            flash('Reseña actualizada.', 'success')
            return redirect(url_for('places.detail', slug=review.place.slug))
        except Exception:
            db.session.rollback()
            logger.exception('Error al editar reseña')
            flash('Error al actualizar la reseña.', 'danger')

    return render_template('reviews/create.html', form=form,
                           place=review.place, edit_mode=True, review=review)


@reviews.route('/<int:review_id>/delete', methods=['POST'])
def delete(review_id):
    review = db.session.get(Review, review_id) or abort(404)
    if not current_user.is_authenticated:
        abort(403)
    if review.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    try:
        slug = review.place.slug
        db.session.delete(review)
        db.session.commit()
        flash('Reseña eliminada.', 'success')
        return redirect(url_for('places.detail', slug=slug))
    except Exception:
        db.session.rollback()
        logger.exception('Error al eliminar reseña')
        flash('Error al eliminar la reseña.', 'danger')
        return redirect(url_for('places.detail', slug=review.place.slug))
