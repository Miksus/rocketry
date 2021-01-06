
from pypipe.core.task import Task

from pathlib import Path
import inspect
import importlib
import subprocess
import re


class ScriptTask(Task):
    """Task that executes a Python script

    ScriptTask("folder/subfolder/main.py")
    ScriptTask("folder/subfolder/mytask.py")
    """
    main_func = "main"

    def execute_action(self, params:dict):
        task_func = self.get_task_func()
        return task_func(**params)

    def get_default_name(self):
        file = self.action
        return '.'.join(file.parts).replace(r'/main.py', '')

    def process_finish(self, *args, **kwargs):
        del self._task_func
        super().process_finish(*args, **kwargs)


    def get_task_func(self):
        if not hasattr(self, "_task_func"):
            # _task_func is cached to faster performance
            task_module = self.get_module(self.action)
            task_func = getattr(task_module, self.main_func)
            self._task_func = task_func
        return self._task_func

    @classmethod
    def from_file(cls, path, **kwargs):
        confs = cls._get_config(cls.get_module(path))
        confs.update(kwargs)
        obj = cls(action=path, **confs)
        return obj

    @classmethod
    def from_project_folder(cls, path, main_file="main.py"):
        """get all tasks from a project folder
        Project folder is a folder with sub folders 
        that contain 'main files' used as
        the actual tasks. 

        Example:
            path structure:
                | my_tasks/
                |____ fetch/
                     |____ prices/
                     |    |____ main.py
                     |____ index/
                          |____ main.py
                          |____ utils.py
                          |____ tickers/
                               |____ main.py
                               |____ utils.py

            ScriptTask.from_project_folder("my_tasks")
            >>> [Task(name=("fetch", "prices"), ...), 
                Task(name=("fetch", "index"), ...), 
                Task(name=("fetch", "index", "tickers"), ...)]
            ....
        """
        root = Path(path)

        tasks = []
        glob = f"**/{main_file}"
        for file in root.glob(glob):
            root_len = len(root.parts)
            name = file.parts[root_len:-1]
            tasks.append(cls.from_file(file, name=name)) 
        return tasks

    @classmethod
    def from_module_folder(cls, path, glob="*.py"):
        """get all tasks from folder
        
        Example:
            path structure:
                | my_tasks/
                |____ fetch_prices.py
                |____ fetch_index.py

            ScriptTask.from_module_folder("my_tasks")
            >>> [Task(name="fetch_prices", ...), Task(name="fetch_index", ...)]
        """
        root = Path(path)

        tasks = []
        for file in root.glob(glob):
            tasks.append(cls.from_file(file, name=file.name.replace(file.suffix, ""))) 
        return tasks

    @staticmethod
    def get_module(path):
        spec = importlib.util.spec_from_file_location("task", path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)
        return task_module

    @staticmethod
    def _get_config(module):
        "Get config from the module"

        confitems = {
            "start_cond": "START_CONDITION",
            "run_cond": "RUN_CONDITION",
            "end_cond": "END_CONDITION",
            "dependent": "DEPENDENT",
            "execution": "EXECUTION",
        }
        confs = {}
        for key, var in confitems.items():
            if hasattr(module, var):
                confs[key] = getattr(module, var)
        return confs

    @property
    def pos_args(self):
        task_func = self.get_task_func()
        sig = inspect.signature(task_func)
        pos_args = [
            val.name
            for name, val in sig.parameters.items()
            if val.kind in (
                inspect.Parameter.POSITIONAL_ONLY, # NOTE: Python <= 3.8 do not have positional arguments, but maybe in the future?
                inspect.Parameter.POSITIONAL_OR_KEYWORD # Keyword argument
            )
        ]
        return pos_args

    @property
    def kw_args(self):
        task_func = self.get_task_func()
        sig = inspect.signature(task_func)
        kw_args = [
            val.name
            for name, val in sig.parameters.items()
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        return kw_args
