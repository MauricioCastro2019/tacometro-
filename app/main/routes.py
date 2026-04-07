from flask import render_template, abort
from flask_login import login_required, current_user
from app.main import main
from app.models.place import Place
from app.models.review import Review


@main.route('/')
def index():
    all_places = Place.query.filter_by(is_active=True).all()
    ranking = sorted(
        [p for p in all_places if p.avg_score is not None],
        key=lambda p: p.avg_score,
        reverse=True
    )[:5]
    return render_template('main/index.html', ranking=ranking)


@main.route('/perfil')
@login_required
def profile():
    reviews = (
        Review.query
        .filter_by(user_id=current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return render_template('main/profile.html', reviews=reviews)
