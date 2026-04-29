import time
from collections import defaultdict
from functools import wraps
from flask import abort, request
from flask_login import current_user

_rate_buckets: dict = defaultdict(list)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


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
