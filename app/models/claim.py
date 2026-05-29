from datetime import datetime, timezone
from app.extensions import db


class PlaceClaim(db.Model):
    __tablename__ = 'place_claims'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(16), default='pending', nullable=False)  # pending, approved, rejected
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    place = db.relationship('Place', backref=db.backref('claims', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('claims', lazy='dynamic'))
