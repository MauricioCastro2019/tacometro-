from flask import render_template, abort, jsonify, request
from flask_login import current_user, login_required
from app.places import places
from app.models.place import Place
from app.models.category import Category
from app.models.favorite import Favorite
from app.extensions import db

PER_PAGE = 24


@places.route('/')
def index():
    sort  = request.args.get('sort', 'score')
    page  = request.args.get('page', 1, type=int)

    all_places = Place.query.filter_by(is_active=True).all()

    if sort == 'name':
        all_places.sort(key=lambda p: p.name.lower())
    elif sort == 'reviews':
        all_places.sort(key=lambda p: p.review_count, reverse=True)
    else:
        all_places.sort(key=lambda p: p.avg_score or 0, reverse=True)

    total = len(all_places)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    paged_places = all_places[start:start + PER_PAGE]

    categories = Category.query.order_by(Category.name).all()

    fav_ids = set()
    reviewed_ids = set()
    if current_user.is_authenticated:
        from app.models.review import Review
        fav_ids = {f.place_id for f in Favorite.query.filter_by(user_id=current_user.id).all()}
        reviewed_ids = {r.place_id for r in Review.query.filter_by(user_id=current_user.id).all()}

    return render_template('places/index.html',
                           places=paged_places,
                           categories=categories,
                           fav_ids=fav_ids,
                           reviewed_ids=reviewed_ids,
                           sort=sort,
                           page=page,
                           total_pages=total_pages,
                           total=total)


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

    # Promedios por criterio para el radar chart
    radar = None
    if reviews:
        n = len(reviews)
        radar = {
            'Sabor':    round(sum(r.taste_score    for r in reviews) / n, 1),
            'Carne':    round(sum(r.meat_score     for r in reviews) / n, 1),
            'Salsa':    round(sum(r.sauce_score    for r in reviews) / n, 1),
            'Tortilla': round(sum(r.tortilla_score for r in reviews) / n, 1),
            'Precio':   round(sum(r.value_score    for r in reviews) / n, 1),
            'Higiene':  round(sum(r.hygiene_score  for r in reviews) / n, 1),
        }

    # Taquerías similares (misma categoría, excluye la actual)
    similar = []
    if place.categories:
        from app.models.place import place_categories
        cat_ids = [c.id for c in place.categories]
        candidates = (
            Place.query
            .filter(Place.is_active == True, Place.id != place.id)
            .join(place_categories, place_categories.c.place_id == Place.id)
            .filter(place_categories.c.category_id.in_(cat_ids))
            .distinct()
            .all()
        )
        similar = sorted(candidates, key=lambda p: p.avg_score or 0, reverse=True)[:3]

    is_fav = False
    user_review = None
    if current_user.is_authenticated:
        is_fav = Favorite.query.filter_by(
            user_id=current_user.id, place_id=place.id
        ).first() is not None
        user_review = Review.query.filter_by(
            user_id=current_user.id, place_id=place.id
        ).first()

    return render_template('places/detail.html', place=place, reviews=reviews,
                           is_fav=is_fav, user_review=user_review,
                           radar=radar, similar=similar)


@places.route('/<int:place_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(place_id):
    place = db.session.get(Place, place_id) or abort(404)
    fav = Favorite.query.filter_by(user_id=current_user.id, place_id=place.id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'favorited': False})
    else:
        db.session.add(Favorite(user_id=current_user.id, place_id=place.id))
        db.session.commit()
        return jsonify({'favorited': True})
