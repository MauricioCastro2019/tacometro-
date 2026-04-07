from flask import render_template, abort
from app.places import places
from app.models.place import Place


@places.route('/')
def index():
    all_places = (
        Place.query
        .filter_by(is_active=True)
        .order_by(Place.name)
        .all()
    )
    # Ordenar por avg_score descendente (None al final)
    all_places.sort(key=lambda p: p.avg_score or 0, reverse=True)
    return render_template('places/index.html', places=all_places)


@places.route('/<slug>')
def detail(slug):
    from app.models.review import Review
    place = Place.query.filter_by(slug=slug, is_active=True).first_or_404()
    reviews = (
        Review.query
        .filter_by(place_id=place.id, is_visible=True)
        .order_by(Review.created_at.desc())
        .limit(20)
        .all()
    )
    return render_template('places/detail.html', place=place, reviews=reviews)
