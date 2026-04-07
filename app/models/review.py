from datetime import datetime, timezone
from app.extensions import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)

    # Puntuaciones (1-10)
    taste_score = db.Column(db.Float, nullable=False)     # sabor      30%
    meat_score = db.Column(db.Float, nullable=False)      # carne      20%
    sauce_score = db.Column(db.Float, nullable=False)     # salsa      15%
    tortilla_score = db.Column(db.Float, nullable=False)  # tortilla   15%
    value_score = db.Column(db.Float, nullable=False)     # precio-cal 10%
    hygiene_score = db.Column(db.Float, nullable=False)   # higiene    10%

    # Texto y media
    comment = db.Column(db.Text)
    image_url = db.Column(db.String(256))

    # Control
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Restricción: un usuario, una reseña por lugar
    __table_args__ = (
        db.UniqueConstraint('user_id', 'place_id', name='uq_user_place_review'),
    )

    @property
    def overall_score(self):
        return round(
            (self.taste_score * 0.30) +
            (self.meat_score * 0.20) +
            (self.sauce_score * 0.15) +
            (self.tortilla_score * 0.15) +
            (self.value_score * 0.10) +
            (self.hygiene_score * 0.10),
            2
        )

    def __repr__(self):
        return f'<Review user={self.user_id} place={self.place_id} score={self.overall_score}>'
