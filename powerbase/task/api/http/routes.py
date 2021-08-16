
from flask import Blueprint, render_template, abort, request, jsonify, abort, current_app
from .utils import parse_url_parameters

# For system info
import pkg_resources
import platform
import psutil
import sys

rest_api = Blueprint(
    'api', 
    __name__,
)

@rest_api.route('/config', methods=['GET'])
def config():
    session = current_app.config["ATLAS_SESSION"]
    if request.method == "GET":
        # Read parameters
        if session.config.get("configs_private", True):
            abort(403) # , "Configurations are inaccessible."
        else:
            return jsonify(session.config)
    return ""

@rest_api.route('/parameters', methods=['GET', "POST"])
@rest_api.route('/parameters/<key>', methods=['PUT', "DELETE"])
def parameters(key=None):
    session = current_app.config["ATLAS_SESSION"]
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
    session = current_app.config["ATLAS_SESSION"]
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
    "Whole log. Name is the name of the logger (ie. powerbase.task.maintain)"
    session = current_app.config["ATLAS_SESSION"]
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


@rest_api.route('/ping', methods=['GET'])
def ping(): 
    "Minimally consuming way to check the server"
    return ""


# Scheduler routes
@rest_api.route('/scheduler/shutdown', methods=['PUT'])
def shut_down(): 
    "Shutdown scheduler"
    # TODO: Test
    session = current_app.config["ATLAS_SESSION"]
    session.scheduler.shut_down()
    return ""


# Informatics
@rest_api.route('/info', methods=['GET'])
@rest_api.route('/info/<name>', methods=['GET'])
def info(name=None): 
    "Get system info"

    # Ideas to include: RAM usage, CPU usage, disk usage, disk free

    # Util funcs (TODO: put to a module)
    def get_python_info():
        return {
            "info": sys.version,
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        }

    def get_os_info():
        info = platform.uname()
        return {
            "info": platform.platform(),
            "system": info.system,
            "machine": info.machine,
            "release": info.release,
            "processor": info.processor,
            "processor_count": psutil.cpu_count(),
            "boot_time": psutil.boot_time(),
        }

    def get_scheduler_info():
        session = current_app.config["ATLAS_SESSION"]
        return {
            "version": pkg_resources.get_distribution("powerbase").version,
            "n_tasks": len(session.tasks),
        }
    
    def get_performance_info():
        "Get CPU, RAM & disk usage percent"
        return {
            "cpu": psutil.cpu_percent() / 100,
            "ram": psutil.virtual_memory().percent / 100,
            "disk": psutil.disk_usage("/").percent / 100,
        }

    def _byte_to_gigabyte(val:int):
        return f"{val / (1024.0 ** 3)} GB"

    def get_ram():
        info = psutil.virtual_memory()
        return {
            "free": _byte_to_gigabyte(info.free),
            "total": _byte_to_gigabyte(info.total),
            "used": _byte_to_gigabyte(info.used)
        }

    def get_disk(partition="/"):
        info = psutil.disk_usage(partition)
        return {
            "free": _byte_to_gigabyte(info.free),
            "total": _byte_to_gigabyte(info.total),
            "used": _byte_to_gigabyte(info.used)
        }

    metrics = {
        "os": get_os_info,
        "python": get_python_info,
        "scheduler": get_scheduler_info,
        "node": platform.node,
        "performance": get_performance_info,
        "disk": get_disk,
        "ram": get_ram,
    }

    if request.method == "GET":
        if name is not None:
            data = metrics[name]()
        else:
            names = request.args.getlist("metric")
            data = {}
            for metric, func in metrics.items():
                if metric in names or not names:
                    data[metric] = func()
        return jsonify(data)
    return ""
