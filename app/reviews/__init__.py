from flask import Blueprint

reviews = Blueprint('reviews', __name__)

from app.reviews import routes  # noqa: F401, E402
