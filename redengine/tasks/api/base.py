
from abc import abstractmethod
from typing import Generator, Iterator, Tuple

from redengine.core import Task
from .resources import call_resource

import time


class APITask(Task):
    """Base class for APIs

    Subclassing this is useful for creating a task
    that communicates user commands to the scheduling
    session in runtime.

    Parameters
    ----------
    delay : int
        Number of seconds to wait before querying
        next set of user commands.

    """
    permanent_task = True

    __register__ = False

    def __init__(self, *args, delay=5, on_startup=True, **kwargs):
        self.delay = delay
        super().__init__(*args, execution="thread", on_startup=on_startup, **kwargs)

    def execute(self, _thread_terminate_):
        self.setup()
        while not _thread_terminate_.is_set():
            self.handle_requests()
            time.sleep(self.delay)
        self.teardown()

    @abstractmethod
    def setup(self):
        "Set up task execution"

    @abstractmethod
    def teardown(self):
        "Tear down task execution"

    @abstractmethod
    def teardown_request(self, resource:str, method:str, data:dict):
        "Tear down handling of a request"

    def handle_requests(self):
        "Handle a cycle of commands (if any)"
        #outputs = []
        for res, method, data in self.get_requests():
            self.call_resource(res, method, data=data)
            self.teardown_request(res, method, data)
        self.teardown_cycle()

    def call_resource(self, resource, method, data):
        output = call_resource(resource, method, data=data)
        if output is not None:
            self.display(output)

    @abstractmethod
    def display(self, outputs:list):
        "Display the outputs of the commands"

    @abstractmethod
    def get_requests(self) -> Iterator[Tuple[str, str, dict]]:
        "Query requests from a file, database etc."
        raise NotImplementedError

    @abstractmethod
    def teardown_cycle(self):
        "Tear down cycle of commands"