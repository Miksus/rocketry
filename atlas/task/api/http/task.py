
from werkzeug.serving import make_server

from flask import Blueprint, render_template, abort, request, jsonify, Flask
from flask.json import JSONEncoder

from atlas import session
from atlas.parse import parse_task
from atlas.core import Task, Parameters
from atlas.core.task import register_task_cls

from pybox.network import get_ip
from .routes import rest_api
from .models import AtlasJSONEncoder

from threading import Thread
import time
import platform
import requests
import pandas as pd
from .utils import check_route_access

@register_task_cls
class HTTPConnection(Task):
    """HTTP Rest API for a scheduler runtime communication
    using Flask. Useful for web UI or communication between
    schedulers.
    Not meant for heavy traffic.

    Examples:
        GET http://127.0.0.1:5000/system/ping
        GET http://127.0.0.1:5000/tasks
        GET http://127.0.0.1:5000/logs
        GET http://127.0.0.1:5000/parameters

        PUT http://127.0.0.1:5000/parameters
        {"mode": "test"}
    """
    # TODO: Token mechanism. A customizable method "is_authenticated(token, resource, method)" that
    # checks whether the token permits the action

    # The listener should be running constantly as long as the scheduler is up
    permanent_task = True

    def __init__(self, access_token=None, host='127.0.0.1', port=5000, delay="1 second", **kwargs):
        self.access_token = access_token
        self.host = host
        self.port = port
        super().__init__(**kwargs)
        self.execution = "thread"
        self.delay = pd.Timedelta(delay).total_seconds()

    # https://flask.palletsprojects.com/en/1.1.x/testing/#testing-json-apis
    def execute_action(self):
        
        self.app = self.create_app()
        server = self.create_server(self.app)
        context = self.app.app_context()
        context.push()

        # Start and run the server
        thread = Thread(target=server.serve_forever)
        thread.start()

        # Wait till termination
        while not self.thread_terminate.is_set():
            time.sleep(self.delay)
        # Note, this may take like 10 seconds
        server.shutdown()
        
    def create_app(self):
        # https://stackoverflow.com/a/45017691/13696660
        app = Flask(__name__)
        app.register_blueprint(rest_api)
        app.json_encoder = AtlasJSONEncoder

        check_route_access.access_token = self.access_token
        app.before_request(check_route_access(app))
        self._set_config(app)
        return app

    def create_server(self, app):
        return make_server(self.host, self.port, app)

    def get_default_name(self):
        return "HTTP-API"

    def _set_config(self, app):
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        app.logger.name = "atlas.api.http" # We don't want it to pollute task logs (would be named as "atlas.task.api.http.task" otherwise)
        app.config["HOST_TASK"] = self


@register_task_cls
class IPAddressPinger(Task):
    
    """Task for pushing the connection information
    to a target host.

    Useful if there is an HTTP interface for the scheduler 
    and the scheduler is set on a dynamic IP or multiple 
    schedulers should be automatically linked to a web UI
    by utilizing the same configuration.

    """
    # TODO: Test
    __status__ = "test"

    def __init__(self, target_url, name=None, ip=None, port=5000, delay="5 minutes", connection_timeout=5, **kwargs):
        super().__init__(**kwargs)

        # Info about where the API is
        self.ip = ip
        self.port = port
        self.name = name
        
        # info about who to send this info to
        self.target_host = target_url

        # Other
        self.execution = "thread"
        self.delay = pd.Timedelta(delay).total_seconds()
        self.connection_timeout = connection_timeout

    def execute_action(self, secret_key):
        while not self.thread_terminate.is_set():
            ip = self.ip if self.ip is not None else get_ip()
            port = self.port
            payload = {
                "name": self.name,
                "node": platform.node(),
                "application": "Atlas",
                "ip": ip,
                "port": port,
                "url": f"http://{ip}:{port}"
            }
            data = jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )
            try:
                requests.post(self.target_host, data=data, timeout=self.connection_timeout)
            except requests.ConnectionError:
                pass
            time.sleep(self.delay)
