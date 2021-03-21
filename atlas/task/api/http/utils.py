
from flask import request, abort

def parse_url_parameters(request):
    params = request.args
    filter_params = {}

    for param in params.keys():
        value = params.getlist(param)
        value = value[0] if len(value) == 1 else value
        if param.startswith("max_"):
            # range is represented as: time = ("2021-01-01", "2021-01-02")
            param_name = param.replace("max_", "")
            pair_value = filter_params.get(param_name, [None])[0]
            filter_params[param_name] = (pair_value, value)
        elif param.startswith("min_"):
            # range is represented as: time = ("2021-01-01", "2021-01-02")
            param_name = param.replace("min_", "")
            pair_value = filter_params.get(param_name, [None])[-1]
            filter_params[param_name] = (value, pair_value)
        else:
            filter_params[param] = value

    return filter_params


def public_route(decorated_function):
    "Decorator to allow all users an access"
    decorated_function.is_public = True
    return decorated_function

def check_route_access(app):
    def wrapper():
        access_token = app.config["ACCESS_TOKEN"]

        token = request.headers.get("Authorization")
        is_public = getattr(app.view_functions.get(request.endpoint, None), 'is_public', False)
        if is_public:
            return

        if token != access_token:
            abort(401)
        return
    return wrapper