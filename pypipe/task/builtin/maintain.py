
from ..types import FuncTask

import socket

import pandas as pd

class FileTriggerTask:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, scheduler):
        tasks_to_run = self.get_triggered_tasks()

        for task in scheduler.tasks:
            if task.name in tasks_to_run:
                self.trigger_task(task)

    def parse_file(self, file):
        if file.suffix == ".csv":
            df = pd.read_csv(file, **self.file_kwds)
            return df.set_index("task_name")["triggered"]


    def get_triggered_tasks(self):
        d = self.parse_file(self.file)

        return [for task_name, status in d.items()]

    def trigger_task(self, task):
        "Force task to run as soon as possible"
        task.force_run = True

class SocetTriggerTask:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), 1234))
        self.socket.listen(5)

    def __call__(self, scheduler):

        clientsocket, address = s.accept()

        msg = clientsocket.recv(1024)
        message = msg.decode("utf-8")

        recd = pickle.loads(msg)

        tasks_to_run = self.get_triggered_tasks()

        for task in scheduler.tasks:
            if task.name in tasks_to_run:
                self.trigger_task(task)

    def get_triggered_tasks(self):
        d = self.parse_file(self.file)

        return [for task_name, status in d.items()]

    def trigger_task(self, task):
        "Force task to run as soon as possible"
        task.force_run = True