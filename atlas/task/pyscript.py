
from atlas.core.task import Task, register_task_cls

from pathlib import Path
import inspect
import importlib
import subprocess
import re
import sys

@register_task_cls
class PyScript(Task):
    """Task that executes a Python script

    PyScript("folder/subfolder/main.py")
    PyScript("folder/subfolder/mytask.py")
    """

    def __init__(self, path, func=None, **kwargs):
        self.path = path
        self.func = "main" if func is None else func
        super().__init__(**kwargs)

    def execute_action(self, **params):

        # Add dir of self.path to sys.path so importing from that dir works
        root = str(Path(self.path).parent)
        sys.path.insert(0, root)

        task_func = self.get_task_func()
        output = task_func(**params)

        sys.path.remove(root)

        return output

    def filter_params(self, params):
        return {
            key: val for key, val in params.items()
            if key in self.kw_args
        }

    def get_default_name(self):
        file = self.path
        return '.'.join(file.parts).replace(r'/main.py', '')

    def process_finish(self, *args, **kwargs):
        if hasattr(self, "_task_func"):
            del self._task_func
        super().process_finish(*args, **kwargs)


    def get_task_func(self):
        
        
        if not hasattr(self, "_task_func"):
            # Add dir of self.path to sys.path so importing from that dir works
            root = str(Path(self.path).parent)
            sys.path.insert(0, root)

            # _task_func is cached to faster performance
            task_module = self.get_module(self.path)
            task_func = getattr(task_module, self.func)
            self._task_func = task_func

            sys.path.remove(root)
        return self._task_func

    @staticmethod
    def get_module(path):
        spec = importlib.util.spec_from_file_location("task", path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)
        return task_module

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
