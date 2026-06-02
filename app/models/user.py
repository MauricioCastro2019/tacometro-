from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(10), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # --- Permisos ---

    @hybrid_property
    def is_admin(self):
        return self.role == 'admin'

    @is_admin.setter
    def is_admin(self, value):
        if value:
            self.role = 'admin'
        elif self.role == 'admin':
            self.role = 'user'

    @is_admin.expression
    def is_admin(cls):
        return cls.role == 'admin'

    def is_owner(self):
        return self.role == 'owner'

    def can_manage_places(self):
        """Puede crear, editar o desactivar taquerías oficiales."""
        return self.role in ('admin',)

    def can_moderate_reviews(self):
        """Puede ocultar o eliminar reseñas de cualquier usuario."""
        return self.role in ('admin',)

    def can_edit_place(self, place):
        """Puede editar esta taquería específica."""
        return self.is_admin or place.owner_id == self.id

    def can_edit_review(self, review):
        """Puede editar esta reseña específica."""
        return self.is_admin or review.user_id == self.id

    def can_delete_review(self, review):
        """Puede eliminar esta reseña específica."""
        return self.is_admin or review.user_id == self.id

    # --- Auth ---

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
