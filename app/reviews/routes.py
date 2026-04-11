from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.reviews import reviews
from app.reviews.forms import ReviewForm
from app.extensions import db
from app.models.place import Place
from app.models.review import Review
from app.utils.image_upload import upload_image


@reviews.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    place_id = request.args.get('place_id', type=int) or request.form.get('place_id', type=int)
    if not place_id:
        abort(400)

    place = db.session.get(Place, place_id) or abort(404)

    existing = Review.query.filter_by(user_id=current_user.id, place_id=place.id).first()
    if existing:
        flash('Ya escribiste una reseña para esta taquería.', 'warning')
        return redirect(url_for('places.detail', slug=place.slug))

    form = ReviewForm()

    if request.method == 'GET':
        form.place_id.data = place.id

    if form.validate_on_submit():
        # Subir foto si se adjuntó una
        image_url = None
        if form.image_file.data and form.image_file.data.filename:
            image_url = upload_image(form.image_file.data)

        review = Review(
            user_id=current_user.id,
            place_id=place.id,
            taste_score=form.taste_score.data,
            meat_score=form.meat_score.data,
            sauce_score=form.sauce_score.data,
            tortilla_score=form.tortilla_score.data,
            value_score=form.value_score.data,
            hygiene_score=form.hygiene_score.data,
            comment=form.comment.data.strip() if form.comment.data else None,
            image_url=image_url,
        )
        db.session.add(review)
        db.session.commit()
        flash('¡Reseña publicada!', 'success')
        return redirect(url_for('places.detail', slug=place.slug))

    return render_template('reviews/create.html', form=form, place=place)
