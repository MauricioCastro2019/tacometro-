from datetime import datetime, timezone
from app.extensions import db


class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name       = db.Column(db.String(128), nullable=False)
    address    = db.Column(db.String(256))
    notes      = db.Column(db.Text)
    status     = db.Column(db.String(16), default='pending', nullable=False)  # pending|approved|rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('suggestions', lazy='dynamic'))

    def __repr__(self):
        return f'<Suggestion {self.name} [{self.status}]>'
