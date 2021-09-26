
import importlib
from typing import Union
from redengine.core.task.base import Task
from redengine.tasks import PyScript
from redengine.parse import parse_task, parse_session
from redengine.pybox.io import read_yaml
from redengine import extensions

import pandas as pd

from pathlib import Path
import time
import logging
import re
import os, sys

class LoaderBase(Task):
    __register__ = False
    default_glob = None

    file_parsers = {
        ".yaml": read_yaml,
    }

    def __init__(self, path=None, glob=None, delay="1 minutes", execution=None, **kwargs):
        execution = "main" if execution is None else execution
        super().__init__(execution=execution, **kwargs)
        self.path = Path.cwd() if path is None else path
        self.glob = glob or self.default_glob
        self.found_items = []

        self.delay = pd.Timedelta(delay).total_seconds()

    def execute(self):
        if self.execution == "main":
            self.load_items()
        else:
            while not self.thread_terminate.is_set():
                self.load_items()
                time.sleep(self.delay)

    def load_items(self):
        prev_found_items = self.found_items.copy()
        self.found_items = []
        root = Path(self.path)
        for conf_path in root.glob(self.glob):
            self.load_file(conf_path, root=root)

        # Delete tasks 
        deleted_items = [old_item for old_item in prev_found_items if old_item not in self.found_items]
        for del_item in deleted_items:
            self.delete_item(del_item)

    def get_default_name(self):
        return type(self).__name__


class ContentLoader(LoaderBase):
    __register__ = False
    default_glob = "**/*.yaml"

    file_parsers = {
        ".yaml": read_yaml,
    }

    def load_file(self, path, root):
        conf = self.read_file(path)
        return self.parse_content(conf, path=path)

    def read_file(self, file) -> Union[list, dict]:
        """Read the file and parse the content to Python object."""
        extension = Path(file).suffix
        if extension not in self.file_parsers:
            raise KeyError(f"No parsing for file type {file}")
        return self.file_parsers[extension](file)


class SessionLoader(ContentLoader):
    """Task that searches other tasks from 
    a directory. All matched files are
    read and the contents are parsed.

    Parameters
    ----------
    path : path-like
        Path to the directory that is searched for the
        tasks.
    glob : str, default="\\*\\*/conftask.yaml"
        Unix pattern that is used to identify the files
        that are parsed with ``redengine.parse.parse_session``.
    delay : str
        Time delay after each cycle of going through the 
        found files. Only usable if ``execution='thread'``
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    It is recommended to execute the task only once at the beginning
    of scheduling session.

    Currently supports:
    
    - YAML files
    """
    default_glob = '**/conftask.yaml'

    def execute(self):
        self.load_items()

    def parse_content(self, conf, path):
        root = Path(path).parent.absolute()
        s = parse_session(
            conf, 
            session=self.session, 
            kwds_fields={"tasks": {"kwds_subparser": {"root":root}}}
        )

    def delete_item(self, item):
        pass


class TaskLoader(ContentLoader):
    """Task that searches other tasks from 
    a directory. All matched files are
    read and the contents are parsed.

    Parameters
    ----------
    path : path-like
        Path to the directory that is searched for the
        tasks.
    glob : str, default="\\*\\*/tasks.yaml"
        Unix pattern that is used to identify the files
        that are read and iteratively parsed with 
        ``redengine.parse.parse_task``.
    delay : str
        Time delay after each cycle of going through the 
        found files. Only usable if ``execution='thread'``
    name_pattern : str
        Regex that is used to filter parsed tasks by name.
        Tasks which names match this pattern are parsed,
        by default no filtering based on name
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.

    Currently supports:
    
    - YAML files
    """
    default_glob = '**/tasks.yaml'
    default_priority = 40 

    def __init__(self, *args, name_pattern=None, **kwargs):
        self.name_pattern = name_pattern
        super().__init__(*args, **kwargs)

    def parse_content(self, conf, path) -> list:
        root = Path(path).parent
        if isinstance(conf, list):
            # List of tasks
            tasks = []
            for task_conf in conf:
                task = self.parse_task(task_conf, root=root)
                if task is not None:
                    tasks.append(task)
            return tasks
        elif isinstance(conf, dict):
            # dict of tasks
            tasks = []
            for name, task_conf in conf.items():
                task_conf["name"] = name
                task = self.parse_task(task_conf, root=root)
                if task is not None:
                    tasks.append(task)
            return tasks
        else:
            raise TypeError("Expected a list of tasks or a dict of task.")

    def parse_task(self, conf:dict, root=None):
        if self.name_pattern:
            name = conf.get('name', '')
            if not re.match(self.name_pattern, name):
                return None

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


class ExtensionLoader(ContentLoader):
    """Task that searches extensions from 
    a directory. All matched files are
    read and the contents are parsed.

    Parameters
    ----------
    path : path-like
        Path to the directory that is searched for the
        extensions.
    glob : str, default="\\*\\*/extensions.yaml"
        Unix pattern that is used to identify the files
        that are parsed to extensions using extensions'
        parsers.
    delay : str
        Time delay after each cycle of going through the 
        found files. Only usable if ``execution='thread'``
    name_pattern : str
        Regex that is used to filter parsed extensions by name.
        Extensions which names match this pattern are parsed,
        by default no filtering based on name
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.

    Currently supports:
    
    - YAML files
    """

    default_glob = '**/extensions.yaml'
    default_priority = 20 # second lowest priority

    def __init__(self, *args, name_pattern=None, **kwargs):
        self.name_pattern = name_pattern
        super().__init__(*args, **kwargs)

    def parse_content(self, conf, path):
        root = Path(path).parent
        if isinstance(conf, list):
            # List of tasks
            return [self.parse_extensions(task_conf, root=root) for task_conf in conf]
        elif isinstance(conf, dict):
            # One task
            task_conf = conf
            return self.parse_extensions(task_conf)
        else:
            raise TypeError("Expected a list of tasks or a dict of task.")

    def parse_extensions(self, conf:dict):
        for key, parser in extensions.PARSERS.items():
            if key in conf:
                ext_conf = conf[key]
                if self.name_pattern:
                    # Filter the names according to the pattern
                    if isinstance(ext_conf, dict):
                        ext_conf = {
                            name: conf
                            for name, conf in ext_conf.items()
                            if re.match(self.name_pattern, name)
                        }
                    else:
                        ext_conf = [
                            conf for conf in ext_conf
                            if re.match(self.name_pattern, conf.get("name", ""))
                        ]
                comps = parser(ext_conf, session=self.session)
        for comp in comps:
            self.found_items.append((comp.__parsekey__, comp.name))

    def delete_item(self, item):
        cls_key, name = item
        self.session.extensions[cls_key][name].delete()


class PyLoader(LoaderBase):
    """Task that searches Python source files matching 
    a given patterns from a given directory. All matched 
    files are simply loaded.

    Parameters
    ----------
    path : path-like
        Path to the directory that is searched for the
        objects.
    glob : str, default="\\*\\*/tasks.py"
        Unix pattern that is used to identify the files
        that are loaded.
    delay : str
        Time delay after each cycle of going through the 
        found files. Only usable if ``execution='thread'``
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.

    """
    default_glob = '**/tasks.py'
    default_priority = 40

    def load_file(self, file, root):
        extension = Path(file).suffix
        if extension != ".py":
            raise KeyError(f"No parsing for file type {file}")
        
        root_path = str(root.absolute())
        if root_path not in sys.path:
            sys.path.append(root_path)
        imp_path = self.to_import_path(file.relative_to(root))
        importlib.import_module(imp_path)
        pass
        #return PyScript.get_module(file)

    def delete_item(self, item):
        pass

    def to_import_path(self, file:Path):
        #file = file.relative_to(root)
        return '.'.join(file.with_suffix("").parts)