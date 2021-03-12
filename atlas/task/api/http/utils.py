
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
