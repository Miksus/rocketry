
from typing import Iterable
from redengine.core.parameters.parameters import Parameters
from .base import APITask
from .models import RedEncoder
import json
from typing import Tuple
from pathlib import Path


class JSONAPI(APITask):
    """API Task to read commands from JSON files

    The JSON file containing the commands should contain
    an array of JSON objects. Each object should have 
    key ``RESOURCE`` and its value should be one of the
    resource classes in ``redengine.tasks.api.resources``.
    Each object should also have a key ``METHOD`` and 
    it may have values ``get``, ``post``, ``patch`` and 
    ``delete`` depending on what is supported by the 
    resource.

    Parameters
    ----------
    path : path-like
        JSON file to listen for commands. Should contain
        an array of objects. See :ref:`resources` for options.
    path_display : path-like, optional
        JSON file where the outputs of GET methods are put.
    path_history : path-like, optional
        File containing JSON lines for write commands so that
        if the session is restarted, the changes can be reapplied.
    **kwargs : dict
        See :py:class:`redengine.core.Task`.


    Examples
    --------

    Minimal example:

    .. code-block:: python

        JSONAPI(path='commands.json')

    Then write to the commands.json

    .. code-block:: json

        [
            {"RESOURCE": "tasks", "METHOD": "get", "code": "def main():\\n    ..."}
        ]
    
    A request JSON object must have keys:
    
    - ``RESOURCE``: specifying the :ref:`resource <resources>` the request is for
    - ``METHOD`` that specifies method of the resource

    """
    def __init__(self, *args, path, path_display=None, path_history=None, **kwargs):
        self.path = path
        self.path_display = path_display
        self.path_history = path_history
        super().__init__(*args, **kwargs)

    def setup(self):
        # Read all commands from store
        if self.path_history is not None and Path(self.path_history).is_file():
            with open(self.path_history, 'r') as f:
                for line in f:
                    data = json.loads(line)

                    self.call_resource(*self.parse_request(data))

    def get_default_name(self):
        return 'api.json'

    def get_requests(self) -> Iterable[Tuple[str, str, dict]]:
        if Path(self.path).is_file():
            with open(self.path, 'r') as f:
                cont = f.read()
                if not cont:
                    return
                cont = json.loads(cont)

            with open(self.path, 'w') as f:
                pass # Emptying the file

            for data in cont:
                yield self.parse_request(data)

    def parse_request(self, data:dict):
        resource = data.pop('RESOURCE')
        method = data.pop('METHOD')
        return resource, method, data

    def format_request(self, resource:str, method:str, data:dict):
        data = data.copy()
        data['RESOURCE'] = resource
        data['METHOD'] = method
        return data

    def display(self, out:list):
        if self.path_display is not None:
            data = json.dumps(out, indent=4, cls=RedEncoder)
            Path(self.path_display).write_text(data)

    def teardown_request(self, resource, method, data:dict):
        if method.lower() != 'get' and self.path_history is not None:
            data = self.format_request(resource, method, data)
            json_data = json.dumps(data)
            with open(self.path_history, 'a') as f:
                f.write(json_data)