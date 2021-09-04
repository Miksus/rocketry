

from powerbase.core.task.base import Task, register_task_cls
from powerbase.tasks import PyScript
from powerbase.parse import parse_task
from pybox.io import read_yaml

import pandas as pd

from pathlib import Path
import time
import logging


@register_task_cls
class YAMLFinder(Task):
    """Task that searches other tasks from 
    a directory. All matched YAML files are
    read and the contents are parsed.

    Parameters
    ----------
    path : path-like
        Path to the directory that is searched for the
        tasks.
    glob : str
        Unix pattern that is used to identify a YAML file
        that is parsed to task(s).
    delay : str
        Time delay after each cycle of going through the 
        found YAML files. Only usable if ``execution='thread'``
    **kwargs : dict
        See :py:class:`powerbase.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.


    """
    def __init__(self, path=None, glob="**/*.yaml", delay="1 minutes", **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self._task_names_old = []
        self.glob = glob

        self.delay = pd.Timedelta(delay).total_seconds()

    def get_default_name(self):
        return type(self).__name__

    def execute_action(self):
        if self.execution == "main":
            self.find_tasks()
        else:
            while not self.thread_terminate.is_set():
                self.find_tasks()
                time.sleep(self.delay)

    def find_tasks(self):
        tasks = []
        task_names = []
        e = None
        for conf_path in Path(self.path).glob(self.glob):
            self.parse_file(conf_path)
        # LOGGER.info(f"Found tasks: {task_names}")

        deleted_tasks = [old for old in self._task_names_old if old not in task_names]
        for del_task in deleted_tasks:
            try:
                del self.session.tasks[del_task]
            except KeyError:
                pass
        
        if e:
            raise e

    def parse_file(self, path):
        root = Path(path).parent
        conf = read_yaml(path)
        if isinstance(conf, list):
            # List of tasks
            return [self.parse_task(task_conf, root=root) for task_conf in conf]
        elif isinstance(conf, dict):
            # One task
            task_conf = conf
            return self.parse_task(task_conf, root=root)
        else:
            raise TypeError("Expected a list of tasks or a dict of task.")

    def parse_task(self, conf:dict, root=None):
        conf["class"] = self._get_class(conf)
        self._set_absolute_path(conf, root=root)
        return parse_task(conf)

    def _get_class(self, conf:dict):
        if "class" in conf:
            return conf.pop("class")
        task_path = Path(conf["path"])
        task_extension = task_path.suffix
        if task_extension == ".py":
            return 'PyScript'
        else:
            # TODO: Add parsing for .ipynb (JupyterTask), .tex (TexTask) etc.
            raise ValueError(f"No task class for task file '{task_extension}'")

    def _set_absolute_path(self, conf:dict, root):
        if "path" in conf and not Path(conf["path"]).is_absolute():
            conf["path"] = root / conf["path"]

    def parse_conf(self, d, root):
        if "class" not in d and "path" in d:
            path = Path(d["path"])
            if path.suffix == ".py":
                cls = "PyScript"
            elif path.suffix == ".tex":
                cls = "TexScript"
            elif path.suffix == ".ipynb":
                cls = "JupyterTask"
            else:
                raise
            d["class"] = cls

        if "path" in d and not Path(d["path"]).is_absolute():
            d["path"] = root / d["path"]

        # TODO: This as argument to the tasks and not like this
        Task.on_exists = "replace"
        task = parse_task(d)
        Task.on_exists = "raise"
        return task

    def _set_env_kwargs(self, conf, env):
        run_on_dev = conf.get("name", "").startswith("dev.")
        run_on_test = conf.get("name", "").startswith("test.")

        if env == "dev":
            # Disable all other tasks than currently on progress
            # and force the on-progress tasks to run
            # (starting with "dev.")
            if run_on_dev:
                conf["force_run"] = True
            else:
                raise TypeError("Env 'dev' can only run tasks starting with 'dev.'")
                # conf["disabled"] = True

        if run_on_dev and env != "dev":
            raise TypeError("Task is meant to be run on env 'dev'")
        elif run_on_test and env != "test":
            raise TypeError("Task is meant to be run on env 'test'")