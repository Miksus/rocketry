
from flask import Blueprint, render_template, abort, request, jsonify, abort
from atlas import session
from .utils import parse_url_parameters

rest_api = Blueprint(
    'api', 
    __name__,
)

@rest_api.route('/parameters', methods=['GET', "POST"])
@rest_api.route('/parameters/<key>', methods=['PUT', "DELETE"])
def parameters(key=None):
    if request.method == "GET":
        # Read parameters
        data = session.parameters
        return jsonify(data)
    elif request.method == "POST" and key is None:
        # Replace existing parameters
        data = request.get_json()
        session.parameters = Paramters(data)

    elif request.method == "POST" and key is not None:
        if key in session.parameters:
            abort(409, "Parameter already exists.")
        data = request.get_json()
        session.parameters[key] = data

    elif request.method == "PUT":
        if not request.is_json:
            raise TypeError(f"Data is not json. Content type: {request.content_type}")
        data = request.get_json()
        session.parameters[key] = data
        
    elif request.method == "DELETE":
        del session.parameters[key]

    return ""

@rest_api.route('/tasks', methods=['GET', "POST"])
@rest_api.route('/tasks/<name>', methods=['GET', "PATCH", "DELETE"])
def tasks(name=None): 
    if request.method == "GET":
        # Read
        is_collection = name is None
        data = session.get_task(name) if not is_collection else session.tasks
        return jsonify(data)
    elif request.method == "POST":
        # Create a task
        raise NotImplementedError("GET .../tasks is not implemented yet.")
        data = request.get_json()
        name = data.get("name", None)
        
        if name is None:
            abort(400, "Task missing name.")
        if name in session.tasks:
            abort(409, "Task already exists.")

        parse_task(data)

    elif request.method == "PATCH":
        if name not in session.tasks:
            abort(409, "Task does not exist.")
        task = session.get_task(name)
        with task.lock:

            # Update/Modify
            data = request.get_json()
            for attr, value in data.items():
                setattr(task, attr, value)
    elif request.method == "DELETE":
        del session.tasks[name]
        # TODO: Delete the task file if user defined PyScript

    return ""

@rest_api.route('/logs/<type_>', methods=['GET'])
@rest_api.route('/logs/<type_>/<logger>', methods=['GET'])
def logs(type_="tasks", logger=None): 
    "Whole log. Name is the name of the logger (ie. atlas.task.maintain)"

    # TODO: Querying
    # query and sort: http://localhost:5001/logs/tasks?sort=+task_name,-start
    # query range: http://localhost:5001/logs/tasks?min_start=2021-01-01&max_start=2021-01-02
    # QUery list: http://localhost:5001/logs/tasks?action=run&action=fail

    if type_ == "tasks":
        loggers = session.get_task_loggers(with_adapters=True)
    elif type_ == "scheduler":
        loggers = session.get_scheduler_loggers(with_adapters=True)
    else:
        raise KeyError(f"Invalid type_: {type_}")
    logger_name = logger

    if request.method == "GET":
        # Read all logs
        # Args are always as lists, we put as strings those suitable
        params = parse_url_parameters(request)
        data = []
        for logger in loggers.values():
            if logger_name is None or name == logger_name:
                data += logger.get_records(**params)

        return jsonify(data)
    return ""


# System
@rest_api.route('/system/shutdown', methods=['PUT'])
def shutdown(): 
    "Shutdown scheduler system"
    raise NotImplementedError
