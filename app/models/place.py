from datetime import datetime, timezone
from app.extensions import db


# Tabla de asociación many-to-many entre taquerías y tipos de taco
place_categories = db.Table(
    'place_categories',
    db.Column('place_id', db.Integer, db.ForeignKey('places.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64), nullable=False, default='León')
    state = db.Column(db.String(64), nullable=False, default='Guanajuato')
    phone = db.Column(db.String(20))
    image_url = db.Column(db.String(512))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Tipos de taco (many-to-many)
    categories = db.relationship(
        'Category', secondary=place_categories,
        backref=db.backref('places', lazy=True)
    )

    # Otras relaciones
    reviews = db.relationship('Review', backref='place', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='place', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def avg_score(self):
        reviews = self.reviews.filter_by(is_visible=True).all()
        if not reviews:
            return None
        return round(sum(r.overall_score for r in reviews) / len(reviews), 2)

    def __repr__(self):
        return f'<Place {self.name}>'
