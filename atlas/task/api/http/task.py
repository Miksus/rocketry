
from werkzeug.serving import make_server

from flask import Blueprint, render_template, abort, request, jsonify, Flask
from flask.json import JSONEncoder

from atlas import session
from atlas.parse import parse_task
from atlas.core import Task, Parameters
from atlas.core.task import register_task_cls

from .routes import rest_api
from .models import AtlasJSONEncoder

from threading import Thread
import time
import pandas as pd
from .utils import check_route_access

@register_task_cls
class HTTPConnection(Task):
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