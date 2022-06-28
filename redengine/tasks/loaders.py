
import importlib
from typing import Union
from pathlib import Path
import time
import re
import sys

import pandas as pd

from redengine.core import Task
from redengine.parse import parse_task
from redengine.pybox.io import read_yaml
from redengine import extensions, Session


class LoaderBase(Task):
    __register__ = False
    default_glob = None

    file_parsers = {
        ".yaml": read_yaml,
    }

    def __init__(self, path=None, glob=None, delay="1 minutes", execution=None, on_startup=True, **kwargs):
        if execution == "process":
            raise ValueError("Loaders cannot be executed as 'process'.")
        execution = "main" if execution is None else execution
        self.path = Path.cwd() if path is None else path
        self.glob = glob or self.default_glob
        self.found_items = []
        self.delay = pd.Timedelta(delay).total_seconds()
        super().__init__(execution=execution, on_startup=on_startup, **kwargs)

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

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}(path={repr(self.path)}, glob={repr(self.glob)}, execution={repr(self.execution)}, name={repr(self.name)}, ...)'


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
        that are parsed with ``redengine.session.Session.from_dict``.
    delay : str
        Time delay after each cycle of going through the 
        found files. Only usable if ``execution='thread'``
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Examples
    --------

    Example of a loaded file, conftask.yaml:

    .. code-block:: yaml

        scheduler:
            # Passed to redengine.core.Scheduler(...)
            ...

        parameters:
            # Passed to redengine.core.Parameters(...)
            env: 'dev'

        tasks:
            - class: TaskLoader
              ...  # Passed to redengine.tasks.loaders.TaskLoader(...)
            - class: FuncTask
              name: 'my-task-1'
              ... # Passed to redengine.tasks.FuncTask(...)

        logging:
            clear_existing: True
            version: 1
            disable_existing_loggers: True
            formatters:
                ...
            handlers:
                ...
            loggers:
                ...

    Then create a loader:

    >>> from redengine.tasks.loaders import SessionLoader
    >>> loader = SessionLoader(glob="**/conftask.yaml")

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
        s = Session.from_dict(
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

    Examples
    --------

    Example of a loaded file, tasks.yaml:

    .. code-block:: yaml

        my-task-1:
            path: 'funcs.py'
            func: 'main'
            start_cond: 'every 10 seconds'
            execution: 'main'
            
        my-task-2:
            path: 'funcs.py'
            func: 'do_things'
            execution: 'process'

    Note that file ``funcs.py`` with functions ``do_things`` 
    and ``main`` should exists in the same directory as where
    this YAML file is in order to the loader to work.

    Then create a loader:

    >>> from redengine.tasks.loaders import TaskLoader
    >>> loader = TaskLoader(glob="**/tasks.yaml")

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    Subprocesses cannot change the state of the session tasks in
    the main thread.

    Currently supports:
    
    - YAML files
    """
    default_glob = '**/tasks.yaml'

    def __init__(self, *args, name_pattern=None, priority=40, **kwargs):
        self.name_pattern = name_pattern
        super().__init__(*args, priority=priority, **kwargs)

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
            return 'FuncTask'
        else:
            # TODO: Add parsing for .ipynb (JupyterTask), .tex (TexTask) etc.
            raise ValueError(f"No task class for task file '{task_extension}'")

    def _set_absolute_path(self, conf:dict, root):
        if "path" in conf and not Path(conf["path"]).is_absolute():
            conf["path"] = root / conf["path"]

    def delete_item(self, item):
        self.session.tasks[item].delete()

class PyLoader(LoaderBase):
    """Python script loader
    
    This task searches Python source files matching 
    a given pattern from a given directory. All matched 
    files are simply imported. If a matched file is 
    already imported, it is reloaded. Note that removed
    content (such as tasks) are unaffected.

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


    Warnings
    --------
    Note that reloading files do not affect on content that is removed.
    If you remove a task from a file that is already imported and this 
    the loader runs, the task won't be removed from the session.
    There are also other caveats in reloading. Please see:
    `importlib.reload <https://docs.python.org/3/library/importlib.html#importlib.reload>`_.

    Examples
    --------

    Example of a loaded file, tasks.py:

    .. code-block:: python

       from redengine.tasks import FuncTask
       from redengine.arguments import FuncArg

       # Some tasks
       @FuncTask(name="my_task_1", start_cond="daily between 08:00 and 15:00")
       def myfunc(my_param):
           ...

       @FuncTask(start_cond="daily between 08:00 and 15:00")
       def my_task_2(my_param):
           ...
         
       # Some arguments
       @FuncArg('my_param_1')
       def myarg():
           ...

       @FuncArg('my_param')
       def my_param_2():
           ...

    Then create a loader:

    >>> from redengine.tasks.loaders import PyLoader
    >>> loader = PyLoader(glob="**/tasks.py")

    Notes
    -----
    ``execution`` can have only values ``main`` and ``thread``.
    If ``execution`` is *main*, the script files are imported
    only once and the task is exited. If ``execution`` is *thread*,
    the task is left running periodically importing and reloading 
    scripts.

    """
    default_glob = '**/tasks.py'

    def __init__(self, *args, priority=40, **kwargs):
        super().__init__(*args, priority=priority, **kwargs)

    def load_file(self, file, root):
        extension = Path(file).suffix
        if extension != ".py":
            raise KeyError(f"No parsing for file type {file}")
        
        root_path = str(root.absolute())
        if root_path not in sys.path:
            sys.path.append(root_path)
        imp_path = self.to_import_path(file.relative_to(root))
        if imp_path in sys.modules:
            # Already imported, reloaded
            mdl = importlib.import_module(imp_path)
            importlib.reload(mdl)
        else:
            # Not imported, import
            importlib.import_module(imp_path)

    def delete_item(self, item):
        pass

    def to_import_path(self, file:Path):
        #file = file.relative_to(root)
        return '.'.join(file.with_suffix("").parts)