from typing import TYPE_CHECKING, Callable, DefaultDict, Dict, Iterator, Optional, Tuple, Union
from threading import Thread
import time

from redengine.core import Parameters
from .resources import Configs, Logs, Parameters, RedResource, Session, Task, Tasks, Dependencies, call_resource

from .base import APITask
from .models import RedEncoder

if TYPE_CHECKING:
    from flask import Flask

class FlaskAPI(APITask):
    """Flask web API for runtime session

    This task hosts a Flask web app using
    waitress and flask_restful. Make sure
    you have these dependencies.

    Parameters
    ----------
    host : str
        Host for the API
    port : int
        Port for the API
    **kwargs : dict
        see :py:class:`redengine.core.Task`

    Examples
    --------

    .. code-block:: python

        from redengine.tasks.api import FlaskAPI
        FlaskAPI()


    Get basic information about the session:

    .. code-block:: console

        curl http://localhost:5000/session

    Get information about a task

    .. code-block:: console

        curl --request POST \ 
             --data '{"class": "CodeTask", "code":"print('hello world')", "start_cond":"daily"}' \ 
             http://localhost:5000/task/my-task-name

    See available resources from 

    .. code-block:: python

        from redengine.tasks.api import RedResource
        RedResource.resources

    """
    def __init__(self, host='127.0.0.1', port=5000, app_config=None, **kwargs):
        super().__init__(**kwargs)
        self.execution = "thread"
        self.host = host
        self.port = port
        self.app_config = {} if app_config is None else app_config

    def get_default_name(self):
        return 'flask-api'

    def setup(self):
        self.app = self.create_app()
        self.server = self.create_server(self.app, self.host, self.port)
        context = self.app.app_context()
        context.push()

        for resource, method, data in self.get_requests():
            call_resource(resource, method, data)

    def execute(self):
        self.setup()
        # Start and run the server
        thread = Thread(target=self.server.run)
        thread.start()

        # Wait till termination
        while not self.thread_terminate.is_set():
            time.sleep(self.delay)
        # Note, this may take like 10 seconds
        self.server.close() # .shutdown()

    def create_app(self):
        # https://stackoverflow.com/a/45017691/13696660
        from flask import Flask
        from flask_restful import Api
        app = Flask("redengine.tasks.api.http")
        app.config.update(self.app_config)
        app.json_encoder = RedEncoder
        self.api = Api(app)

        app.before_request(self.authenticate)
        self.add_url_rules(app)
        return app

    def create_server(self, app, host, port):
        from waitress import create_server
        return create_server(app, host=host, port=port)

    def add_url_rules(self, app:'Flask'):
        from flask_restful import Resource
        def to_rest(cls):
            new_cls = type(f'Http{cls.__name__}', (cls, Resource), {'_api': self})
            setattr(new_cls, 'get_kwargs', self._resource_wrapper)
            setattr(new_cls, 'format_output', self.format_output)
            return new_cls

        self.api.add_resource(to_rest(Task), '/tasks/<string:name>')
        self.api.add_resource(to_rest(Configs), '/configs')
        self.api.add_resource(to_rest(Parameters), '/parameters')
        self.api.add_resource(to_rest(Session), '/session')
        self.api.add_resource(to_rest(Tasks), '/tasks')
        self.api.add_resource(to_rest(Logs), '/logs')
        self.api.add_resource(to_rest(Dependencies), '/dependencies')

    def get_endpoint_kwds(self, resource):
        from flask import request
        if request.method == 'GET':
            return list(request.args.items(multi=True))
        return request.get_json()

    @staticmethod
    def _resource_wrapper(resource:RedResource):
        # Note that this is actually resource's method
        from flask import request
        self = resource._api
        kwargs = self.get_endpoint_kwds(resource)
        self.store_request(resource, method=request.method, data=kwargs)
        return kwargs

    @staticmethod
    def format_output(resource, output):
        from flask import jsonify
        return jsonify(output)

    def authenticate(self):
        "Authenticate the user"

    def store_request(self, resource:RedResource, method:str, data:Union[list, dict, None]):
        """Store the request to reimplement after restart
        
        Parameters
        ----------
        resources : RedResource
            Resource that was requested
        method : str
            HTTP method. Should correspond on the method
            on the resource.
        data : list, dict
            Data for the request.
        """
    
    def get_requests(self) -> Iterator[Tuple[str, str, Union[list, dict]]]:
        """Get stored requests to reimplement after restart
        
        Returns
        -------
        tuple
            The first argument is the resource name (ie. ``Task``), 
            second argument is the method name (ie. ``POST``) and 
            third is the data to pass as keyword arguments to the 
            resource
        """
        yield from ()