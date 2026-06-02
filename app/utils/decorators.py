import time
from collections import defaultdict
from functools import wraps
from flask import abort, request, redirect, url_for, flash
from flask_login import current_user

_rate_buckets: dict = defaultdict(list)


def admin_required(f):
    """Permite acceso solo a admins.
    - Sin sesión → redirect a login con ?next=<url actual>
    - Autenticado pero sin permisos → 403
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def owner_or_admin_required(get_place_fn):
    """Decorador de fábrica: verifica que el usuario sea dueño del lugar o admin.

    Uso:
        @owner_or_admin_required(lambda: Place.query.filter_by(slug=slug).first_or_404())
        def mi_vista(slug): ...

    O en su lugar usa el helper _require_owner_or_admin(place) dentro de la vista
    cuando ya tienes el objeto place.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            place = get_place_fn()
            if not current_user.can_edit_place(place):
                flash('No tienes permisos para gestionar esta taquería.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def rate_limit(max_calls: int, period: int):
    """Simple in-memory rate limiter. max_calls per period (seconds) per IP."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            key = f.__name__ + ':' + (request.remote_addr or 'unknown')
            now = time.monotonic()
            _rate_buckets[key] = [t for t in _rate_buckets[key] if now - t < period]
            if len(_rate_buckets[key]) >= max_calls:
                abort(429)
            _rate_buckets[key].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator
