

from redengine.core.task.base import Task
from redengine.tasks import PyScript
from redengine.parse import parse_task, parse_session
from redengine.pybox.io import read_yaml
from redengine import extensions

import pandas as pd

from pathlib import Path
import time
import logging

class YAMLLoaderBase(Task):
    __register__ = False
    default_glob = '**/*.yaml'
    def __init__(self, path=None, glob=None, delay="1 minutes", execution=None, **kwargs):
        execution = "main" if execution is None else execution
        super().__init__(execution=execution, **kwargs)
        self.path = Path.cwd() if path is None else path
        self.glob = glob or self.default_glob
        self.found_items = []

        self.delay = pd.Timedelta(delay).total_seconds()

    def execute_action(self):
        if self.execution == "main":
            self.parse_items()
        else:
            while not self.thread_terminate.is_set():
                self.parse_items()
                time.sleep(self.delay)

    def parse_items(self):
        prev_found_items = self.found_items.copy()
        self.found_items = []
        for conf_path in Path(self.path).glob(self.glob):
            self.parse_file(conf_path)

        # Delete tasks 
        deleted_items = [old_item for old_item in prev_found_items if old_item not in self.found_items]
        for del_item in deleted_items:
            self.delete_item(del_item)

    def get_default_name(self):
        return type(self).__name__


class YAMLLoader(YAMLLoaderBase):
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
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    It is recommended to execute the task only once at the beginning
    of scheduling session
    """
    default_glob = '**/conftask.yaml'

    def execute_action(self):
        self.parse_items()

    def parse_file(self, path):
        root = Path(path).parent.absolute()
        conf = read_yaml(path)
        s = parse_session(
            conf, 
            session=self.session, 
            kwds_fields={"tasks": {"kwds_subparser": {"root":root}}}
        )

    def delete_item(self, item):
        pass


class YAMLTaskLoader(YAMLLoaderBase):
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
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.
    """
    default_glob = '**/task*.yaml'
    default_priority = 40 
    def parse_file(self, path):
        root = Path(path).parent
        conf = read_yaml(path)
        if isinstance(conf, list):
            # List of tasks
            return [self.parse_task(task_conf, root=root) for task_conf in conf]
        elif isinstance(conf, dict):
            # dict of tasks
            tasks = []
            for name, task_conf in conf.items():
                task_conf["name"] = name
                tasks.append(self.parse_task(task_conf, root=root))
            return tasks
        else:
            raise TypeError("Expected a list of tasks or a dict of task.")

    def parse_task(self, conf:dict, root=None):
        conf["class"] = self._get_class(conf)
        self._set_absolute_path(conf, root=root)
        conf["on_exists"] = 'replace'
        task = parse_task(conf, session=self.session)
        self.found_items.append(task.name)
        return task

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

    def delete_item(self, item):
        self.session.tasks[item].delete()


class YAMLExtensionLoader(YAMLLoaderBase):

    default_glob = '**/ext*.yaml'
    default_priority = 20 # second lowest priority

    def parse_file(self, path):
        root = Path(path).parent
        conf = read_yaml(path)
        if isinstance(conf, list):
            # List of tasks
            return [self.parse_extension(task_conf, root=root) for task_conf in conf]
        elif isinstance(conf, dict):
            # One task
            task_conf = conf
            return self.parse_extension(task_conf)
        else:
            raise TypeError("Expected a list of tasks or a dict of task.")

    def parse_extension(self, conf):
        for key, parser in extensions.PARSERS.items():
            if key in conf:
                comps = parser(conf[key], session=self.session)
        for comp in comps:
            self.found_items.append((comp.__parsekey__, comp.name))

    def delete_item(self, item):
        cls_key, name = item
        self.session.extensions[cls_key][name].delete()