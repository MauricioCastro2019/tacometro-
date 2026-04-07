from datetime import datetime, timezone
from app.extensions import db


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
    image_url = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Clave foránea
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Relaciones
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
