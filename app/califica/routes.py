import json
import math
import logging
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user
from app.califica import califica
from app.extensions import db
from app.models.place import Place
from app.models.review import Review
from app.models.category import Category
from app.utils.image_upload import upload_image
from app.utils.slugify import slugify

logger = logging.getLogger(__name__)

ESPECIALIDADES_FORM = [
    ('Pastor',      '🌮'),
    ('Suadero',     '🥩'),
    ('Tripa',       '🌀'),
    ('Bistec',      '🥩'),
    ('Arrachera',   '🔥'),
    ('Costilla',    '🍖'),
    ('Birria',      '🍲'),
    ('Guisado',     '🍳'),
    ('Canasta',     '🧺'),
    ('Barbacoa',    '🐑'),
    ('Cabeza',      '🐮'),
    ('Carnitas',    '🐷'),
    ('Cecina',      '🥓'),
    ('Chorizo',     '🌶️'),
    ('Campechano',  '🌮'),
    ('Pescado',     '🐟'),
    ('Mariscos',    '🦐'),
    ('Vegetariano', '🌱'),
    ('Variados',    '🌮'),
    ('Otro',        '❓'),
]


@califica.route('/')
def inicio():
    """Paso 1: Buscar o elegir taquería."""
    query = request.args.get('q', '').strip()
    places = []
    if query:
        try:
            places = Place.query.filter(
                Place.is_active == True,
                Place.name.ilike(f'%{query}%')
            ).order_by(Place.name).limit(10).all()
        except Exception:
            logger.exception('Error buscando taquerías')
    return render_template('califica/paso1.html', query=query, places=places)


@califica.route('/nueva', methods=['GET', 'POST'])
def nueva_taqueria():
    """Paso 2: Agregar nueva taquería (si no existe)."""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre de la taquería es obligatorio.', 'danger')
            return redirect(url_for('califica.nueva_taqueria'))

        try:
            slug = slugify(nombre)
            existing = Place.query.filter_by(slug=slug).first()
            if existing:
                flash(f'Ya existe "{existing.name}". ¿Es esta taquería?', 'warning')
                return redirect(url_for('califica.rate', place_id=existing.id))

            foto_url = None
            foto = request.files.get('foto_lugar')
            if foto and foto.filename:
                foto_url = upload_image(foto)

            cats = []
            for esp in request.form.getlist('especialidad'):
                esp = esp.strip()
                if not esp:
                    continue
                cat = Category.query.filter_by(name=esp).first()
                if not cat:
                    cat = Category(name=esp, slug=slugify(esp), icon='')
                    db.session.add(cat)
                cats.append(cat)

            otro_texto = request.form.get('otro_texto', '').strip()
            if otro_texto:
                cats = [c for c in cats if c.name != 'Otro']
                cat = Category.query.filter_by(name=otro_texto).first()
                if not cat:
                    cat = Category(name=otro_texto, slug=slugify(otro_texto), icon='🌮')
                    db.session.add(cat)
                if cat not in cats:
                    cats.append(cat)
            else:
                cats = [c for c in cats if c.name != 'Otro']

            hora_apertura = request.form.get('hora_apertura', '').strip()
            hora_cierre = request.form.get('hora_cierre', '').strip()
            _dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
            horario = {}
            for dia in _dias:
                if request.form.get(f'dia_{dia}') and hora_apertura and hora_cierre:
                    horario[dia] = {'abre': hora_apertura, 'cierra': hora_cierre}

            lat = lng = None
            try:
                lat_s = request.form.get('latitud', '').strip()
                lng_s = request.form.get('longitud', '').strip()
                if lat_s and lng_s:
                    lat, lng = float(lat_s), float(lng_s)
            except (ValueError, TypeError):
                pass

            place = Place(
                name=nombre,
                slug=slug,
                address=request.form.get('direccion', '').strip() or None,
                description=request.form.get('comentario', '').strip() or None,
                image_url=foto_url,
                latitude=lat,
                longitude=lng,
                is_active=True,
                horario=json.dumps(horario) if horario else None,
            )
            place.categories = cats
            db.session.add(place)
            db.session.commit()

            flash(f'¡"{nombre}" registrada! Ahora califícala.', 'success')
            return redirect(url_for('califica.rate', place_id=place.id))

        except Exception:
            db.session.rollback()
            logger.exception('Error al crear taquería desde flujo califica')
            flash('Error al registrar la taquería. Intenta de nuevo.', 'danger')

    nombre_sugerido = request.args.get('nombre', '')
    return render_template('califica/nueva_taqueria.html',
                           especialidades=ESPECIALIDADES_FORM,
                           nombre_sugerido=nombre_sugerido)


@califica.route('/rate/<int:place_id>', methods=['GET', 'POST'])
def rate(place_id):
    """Paso 3: Calificar experiencia."""
    place = db.session.get(Place, place_id)
    if not place:
        flash('Taquería no encontrada.', 'danger')
        return redirect(url_for('califica.inicio'))

    if current_user.is_authenticated:
        existing = Review.query.filter_by(
            user_id=current_user.id, place_id=place.id
        ).first()
        if existing:
            flash('Ya calificaste esta taquería. Puedes editar tu reseña.', 'info')
            return redirect(url_for('califica.confirmacion', review_id=existing.id))

    if request.method == 'POST':
        try:
            errores = []

            def get_score(campo, label):
                val = request.form.get(campo)
                try:
                    v = int(val)
                    if 1 <= v <= 5:
                        return float(v)
                except (ValueError, TypeError):
                    pass
                errores.append(f'{label}: selecciona entre 1 y 5 estrellas.')
                return None

            sabor = get_score('sabor', 'Sabor')
            salsa = get_score('salsa', 'Salsa')
            servicio = get_score('servicio', 'Servicio')
            precio_calidad = get_score('precio_calidad', 'Precio/calidad')
            higiene = get_score('higiene', 'Higiene')

            if errores:
                for e in errores:
                    flash(e, 'danger')
                return render_template('califica/rate.html', place=place)

            foto_url = None
            foto = request.files.get('foto_comida')
            if foto and foto.filename:
                foto_url = upload_image(foto)

            volveria_raw = request.form.get('volveria', '')
            volveria = True if volveria_raw == 'si' else (False if volveria_raw == 'no' else None)

            gasto = None
            try:
                gasto_s = request.form.get('gasto_aproximado', '').strip()
                if gasto_s:
                    gasto = float(gasto_s)
            except (ValueError, TypeError):
                pass

            nickname = (request.form.get('nickname', '').strip() or None)
            if nickname:
                nickname = nickname[:64]
            comentario = request.form.get('comentario', '').strip() or None
            tacos_probados = (request.form.get('tacos_probados', '').strip() or None)
            if tacos_probados:
                tacos_probados = tacos_probados[:256]
            salsas_probadas = (request.form.get('salsas_probadas', '').strip() or None)
            if salsas_probadas:
                salsas_probadas = salsas_probadas[:256]
            bebidas = (request.form.get('bebidas', '').strip() or None)
            if bebidas:
                bebidas = bebidas[:128]
            postres = (request.form.get('postres', '').strip() or None)
            if postres:
                postres = postres[:128]

            review = Review(
                user_id=current_user.id if current_user.is_authenticated else None,
                nickname=nickname,
                place_id=place.id,
                sabor=sabor,
                salsa=salsa,
                servicio=servicio,
                precio_calidad=precio_calidad,
                higiene=higiene,
                comentario=comentario,
                foto_comida=foto_url,
                volveria=volveria,
                gasto_aproximado=gasto,
                tacos_probados=tacos_probados,
                salsas_probadas=salsas_probadas,
                bebidas=bebidas,
                postres=postres,
            )
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('califica.confirmacion', review_id=review.id))

        except Exception:
            db.session.rollback()
            logger.exception('Error al guardar calificación')
            flash('Error al guardar tu calificación. Intenta de nuevo.', 'danger')

    return render_template('califica/rate.html', place=place)


@califica.route('/ok/<int:review_id>')
def confirmacion(review_id):
    """Paso 4: Confirmación."""
    review = db.session.get(Review, review_id)
    if not review:
        return redirect(url_for('main.index'))
    place = review.place
    return render_template('califica/confirmacion.html', review=review, place=place)


@califica.route('/api/buscar')
def api_buscar():
    """API JSON para búsqueda de taquerías."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        places = Place.query.filter(
            Place.is_active == True,
            Place.name.ilike(f'%{q}%')
        ).limit(10).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'address': p.address or '',
            'avg_score': p.avg_score,
            'rate_url': url_for('califica.rate', place_id=p.id),
        } for p in places])
    except Exception:
        logger.exception('Error en api_buscar')
        return jsonify([])


@califica.route('/api/cercanas')
def api_cercanas():
    """API JSON: taquerías con coords ordenadas por distancia."""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Coordenadas inválidas'}), 400

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    try:
        places = Place.query.filter(
            Place.is_active == True,
            Place.latitude.isnot(None),
            Place.longitude.isnot(None)
        ).all()

        result = sorted([{
            'id': p.id,
            'name': p.name,
            'address': p.address or '',
            'avg_score': p.avg_score,
            'dist': round(haversine(lat, lng, p.latitude, p.longitude), 2),
            'rate_url': url_for('califica.rate', place_id=p.id),
            'detail_url': url_for('places.detail', slug=p.slug),
        } for p in places], key=lambda x: x['dist'])

        return jsonify(result[:10])
    except Exception:
        logger.exception('Error en api_cercanas')
        return jsonify([])
