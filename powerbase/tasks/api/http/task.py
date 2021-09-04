
from werkzeug.serving import make_server

from flask import Blueprint, render_template, abort, request, jsonify, Flask
from flask.json import JSONEncoder
import jwt

from powerbase.parse import parse_task
from powerbase.core import Task, Parameters
from powerbase.core.task import register_task_cls

from pybox.network import get_ip
from .routes import rest_api
from .models import PowerbaseJSONEncoder

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

    def __init__(self, delay="1 second", **kwargs):
        super().__init__(**kwargs)
        self.execution = "thread"
        self.delay = pd.Timedelta(delay).total_seconds()

    # https://flask.palletsprojects.com/en/1.1.x/testing/#testing-json-apis
    def execute_action(self, access_token=None):

        # TODO: refetch the http_api parameters in while loop
        host = self.get_host()
        port = self.get_port()
        access_token = self.get_access_token(access_token)
        
        self.app = self.create_app(access_token=access_token)
        server = self.create_server(self.app, host, port)
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
        
    def get_host(self) -> str:
        "Get IP to host the app (by default uses localhost)"
        return self.session.config.get("http_api_host", '127.0.0.1')

    def get_port(self) -> int:
        "Get port to host the app"
        return self.session.config.get("http_api_port", 5000)

    def get_access_token(self, access_token):
        "Get access token for authentication (if None, no access tokens used)"
        conf_access_token = self.session.config.get("http_api_access_token", None)
        return conf_access_token if conf_access_token is not None else access_token

    def create_app(self, **kwargs):
        # https://stackoverflow.com/a/45017691/13696660
        app = Flask("powerbase.api")
        app.register_blueprint(rest_api)
        app.json_encoder = PowerbaseJSONEncoder
        app.config["ATLAS_SESSION"] = self.session

        app.before_request(check_route_access(app))
        self._set_config(app, **kwargs)
        return app

    def create_server(self, app, host, port):
        return make_server(host, port, app)

    def get_default_name(self):
        return "HTTP-API"

    def _set_config(self, app, access_token=None):
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        app.logger.name = "powerbase.api.http" # We don't want it to pollute task logs (would be named as "powerbase.tasks.api.http.task" otherwise)
        app.config["HOST_TASK"] = self
        app.config["ACCESS_TOKEN"] = access_token


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

    def __init__(self, target_url, app_name=None, delay="5 minutes", connection_timeout=5, **kwargs):
        super().__init__(**kwargs)

        # Info about where the API is
        self.app_name = app_name
        
        # info about who to send this info to
        self.target_host = target_url

        # Other
        self.execution = "thread"
        self.delay = pd.Timedelta(delay).total_seconds()
        self.connection_timeout = connection_timeout

    def execute_action(self, http_api:dict):
        # TODO: refetch the http_api parameters in while loop
        api_info = http_api

        host = api_info["host"]
        port = api_info["port"]
        secret_key = api_info["api_secret"]
        access_token = api_info.get("access_token", None)

        while not self.thread_terminate.is_set():
            host = get_ip() if host is None or host == "0.0.0.0" else host
            name = self.app_name if self.app_name is not None else platform.node()

            payload = {
                "name": name,
                "node": platform.node(),
                "application": "Powerbase",
                "host": host,
                "port": port,
                "url": f"http://{host}:{port}",
                "token": access_token,
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
