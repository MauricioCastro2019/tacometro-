from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required
from app.admin import admin
from app.admin.forms import PlaceForm
from app.extensions import db
from app.models.category import Category
from app.models.place import Place
from app.utils.decorators import admin_required
from app.utils.slugify import slugify


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
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Place.query.filter_by(slug=slug).first():
            flash('Ya existe una taquería con ese nombre.', 'danger')
        else:
            place = Place(
                name=form.name.data,
                slug=slug,
                description=form.description.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_url=form.image_url.data or None,
                category_id=form.category_id.data,
                is_active=form.is_active.data,
            )
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
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        new_slug = slugify(form.name.data)
        existing = Place.query.filter_by(slug=new_slug).first()
        if existing and existing.id != place.id:
            flash('Ya existe una taquería con ese nombre.', 'danger')
        else:
            place.name = form.name.data
            place.slug = new_slug
            place.description = form.description.data
            place.address = form.address.data
            place.city = form.city.data
            place.state = form.state.data
            place.phone = form.phone.data
            place.image_url = form.image_url.data or None
            place.category_id = form.category_id.data
            place.is_active = form.is_active.data
            db.session.commit()
            flash(f'Taquería "{place.name}" actualizada.', 'success')
            return redirect(url_for('admin.index'))

    return render_template('admin/place_form.html', form=form, title='Editar taquería', place=place)
