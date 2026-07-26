from functools import wraps
from flask_login import current_user


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return "Unauthorized", 401
            if current_user.role not in allowed_roles:
                return "Forbidden", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
