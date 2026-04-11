from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    icon = db.Column(db.String(64))

    # La relación inversa 'places' la crea el backref en Place.categories

    def __repr__(self):
        return f'<Category {self.name}>'
