from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.main import main
from app.models.place import Place
from app.models.review import Review
from app.extensions import db


@main.route('/')
def index():
    all_places = Place.query.filter_by(is_active=True).all()
    ranking = sorted(
        [p for p in all_places if p.avg_score is not None],
        key=lambda p: p.avg_score,
        reverse=True
    )[:5]
    total_places = len(all_places)
    total_reviews = Review.query.count()
    return render_template('main/index.html', ranking=ranking,
                           total_places=total_places, total_reviews=total_reviews)


@main.route('/perfil/cambiar-contrasena', methods=['POST'])
@login_required
def change_password():
    current_pw  = request.form.get('current_password', '')
    new_pw      = request.form.get('new_password', '')
    confirm_pw  = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        flash('La contraseña actual es incorrecta.', 'danger')
    elif len(new_pw) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
    elif new_pw != confirm_pw:
        flash('Las contraseñas no coinciden.', 'danger')
    else:
        current_user.set_password(new_pw)
        db.session.commit()
        flash('Contraseña actualizada correctamente.', 'success')
    return redirect(url_for('main.profile'))


@main.route('/perfil')
@login_required
def profile():
    from app.models.favorite import Favorite
    from app.models.place import Place
    reviews = (
        Review.query
        .filter_by(user_id=current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    fav_places = (
        Place.query
        .join(Favorite, Favorite.place_id == Place.id)
        .filter(Favorite.user_id == current_user.id, Place.is_active == True)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return render_template('main/profile.html', reviews=reviews, fav_places=fav_places)


@main.route('/mapa')
def mapa():
    return render_template('main/map.html')


@main.route('/sugerir', methods=['GET', 'POST'])
def suggest():
    from app.models.suggestion import Suggestion
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        notes   = request.form.get('notes', '').strip()
        if not name:
            flash('El nombre de la taquería es obligatorio.', 'danger')
            return redirect(url_for('main.suggest'))
        sug = Suggestion(
            name=name,
            address=address or None,
            notes=notes or None,
            user_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(sug)
        db.session.commit()
        flash('¡Gracias por tu sugerencia! El equipo la revisará pronto.', 'success')
        return redirect(url_for('places.index'))
    return render_template('main/suggest.html')


@main.route('/robots.txt')
def robots():
    from flask import Response
    txt = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /auth/\n"
    return Response(txt, mimetype='text/plain')


@main.route('/sitemap.xml')
def sitemap():
    from flask import Response
    host = request.host_url.rstrip('/')
    places = Place.query.filter_by(is_active=True).all()
    urls = [f'<url><loc>{host}/</loc></url>',
            f'<url><loc>{host}/places</loc></url>',
            f'<url><loc>{host}/mapa</loc></url>']
    for p in places:
        urls.append(f'<url><loc>{host}/places/{p.slug}</loc></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + ''.join(urls) + '</urlset>')
    return Response(xml, mimetype='application/xml')


@main.route('/api/places')
def api_places():
    places = Place.query.filter_by(is_active=True).all()
    result = []
    for p in places:
        result.append({
            'id': p.id,
            'name': p.name,
            'address': p.address or '',
            'category': ', '.join(c.name for c in p.categories) if p.categories else '',
            'avg_score': p.avg_score,
            'review_count': p.review_count,
            'lat': p.latitude,
            'lng': p.longitude,
            'url': f'/places/{p.slug}',
        })
    return jsonify(result)
