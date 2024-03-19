from flask import request, abort
from functools import wraps
from flask_login import current_user


class Helper:
    @staticmethod
    def check_url_var(varname):
        if request.method == 'GET':
            if request.args:
                data = request.args[varname]
                return data
        return None


def is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        return abort(401)
    return decorated_function

