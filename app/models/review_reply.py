from datetime import datetime, timezone
from app.extensions import db


class ReviewReply(db.Model):
    __tablename__ = 'review_replies'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    review = db.relationship('Review', backref=db.backref('reply', uselist=False))
    owner = db.relationship('User', backref=db.backref('review_replies', lazy='dynamic'))
