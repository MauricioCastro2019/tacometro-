from datetime import datetime, timezone
from app.extensions import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)

    # user_id nullable para permitir reseñas con nickname (beta sin login obligatorio)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)

    # Nombre de usuario para reseñas anónimas
    nickname = db.Column(db.String(64), nullable=True)

    # Puntuaciones 1-5
    sabor = db.Column(db.Float, nullable=False)           # 35%
    salsa = db.Column(db.Float, nullable=False)           # 25%
    servicio = db.Column(db.Float, nullable=False)        # 15%
    precio_calidad = db.Column(db.Float, nullable=False)  # 15%
    higiene = db.Column(db.Float, nullable=False)         # 10%

    # Texto y media
    comentario = db.Column(db.Text)
    foto_comida = db.Column(db.String(512))

    # Campos adicionales
    volveria = db.Column(db.Boolean, nullable=True)
    gasto_aproximado = db.Column(db.Float, nullable=True)
    tacos_probados = db.Column(db.String(256), nullable=True)

    # Control
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def overall_score(self):
        return round(
            (self.sabor * 0.35) +
            (self.salsa * 0.25) +
            (self.precio_calidad * 0.15) +
            (self.servicio * 0.15) +
            (self.higiene * 0.10),
            1
        )

    @property
    def display_name(self):
        if self.author:
            return self.author.username
        return self.nickname or 'Anónimo'

    def __repr__(self):
        return f'<Review place={self.place_id} score={self.overall_score}>'
