from flask import Blueprint

places = Blueprint('places', __name__)

from app.places import routes  # noqa: F401, E402
