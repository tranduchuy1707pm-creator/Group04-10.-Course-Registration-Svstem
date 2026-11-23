from functools import wraps
from flask import session, abort


def role_required(role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if not session.get("user_id"):
                abort(401)

            user_role = str(
                session.get("role", "")
            ).lower()

            if user_role != role.lower():
                abort(403)

            return function(*args, **kwargs)

        return wrapper

    return decorator
