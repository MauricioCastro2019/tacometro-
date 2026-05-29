from flask import Blueprint

owner = Blueprint('owner', __name__)

from app.owner import routes  # noqa: F401, E402
