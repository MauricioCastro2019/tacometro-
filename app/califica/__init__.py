from flask import Blueprint

califica = Blueprint('califica', __name__)

from app.califica import routes  # noqa: E402, F401
