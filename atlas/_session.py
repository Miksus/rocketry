

"""
Utilities for getting information 
about the scehuler/task/parameters etc.
"""

import logging
from pathlib import Path
import pandas as pd

from atlas.core.log import TaskAdapter
from atlas.core import Scheduler, Task, BaseCondition, Parameters

from atlas.log import CsvHandler, CsvFormatter
from atlas.config import get_default

class _Session:
    """Collection of the relevant data and methods
    of the atlas ecosystem. 

    Returns:
        [type]: [description]
    """
    # TODO:
    #   .reset() Put logger to default, clear Parameters, Schedulers and Tasks
    #   .
    
    def __init__(self):
        self.tasks = {}
        self.parameters = Parameters()
        self.scheduler = None


    def get_tasks(self) -> list:
        return self.tasks.values()

    def get_task(self, task):
        return self.tasks[task] if not isinstance(task, Task) else task

    @staticmethod
    def get_task_loggers(with_adapters=True) -> dict:
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger 
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith(Task._logger_basename) 
            and not isinstance(logger, logging.PlaceHolder)
            and not name.endswith("_process") # No private
        }

    @staticmethod
    def get_scheduler_loggers(with_adapters=True) -> dict:
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger  
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith(Scheduler._logger_basename) 
            and not isinstance(logger, logging.PlaceHolder)
            and not name.startswith("_") # No private
        }

# Log data
    def get_task_log(self, **kwargs):
        loggers = self.get_task_loggers(with_adapters=True)
        dfs = [
            logger.get_records(**kwargs)
            for logger in loggers.values()
        ]
        return pd.concat(dfs, axis=0)

    def get_scheduler_log(self, **kwargs):
        loggers = self.get_scheduler_loggers(with_adapters=True)
        dfs = [
            logger.get_records(**kwargs)
            for logger in loggers.values()
        ]
        return pd.concat(dfs, axis=0)

    def get_task_run_info(self, **kwargs):
        df = self.get_task_log(**kwargs)
        return get_run_info(df)

    def get_task_info(self):
        return pd.DataFrame([
            {
                "name": name, 
                "priority": task.priority, 
                "timeout": task.timeout, 
                "start_condition": task.start_cond, 
                "end_condition": task.end_cond
            } for name, task in session.get_tasks().items()
        ])

    def reset(self):
        "Set Pypipe ecosystem to default settings (clearing tasks etc)"
        get_default("csv_logging")
        self.tasks = {}
        self.parameters = Parameters()
        
    def clear(self):
        "Clear tasks, parameters etc. of the session"
        self.tasks = {}
        self.parameters = Parameters()
        self.scheduler = None

    def __getstate__(self):
        # NOTE: When a process task is executed, it will pickle
        # the task.session. Therefore removing unpicklable here.
        state = self.__dict__.copy()
        state["tasks"] = {}
        state["scheduler"] = None
        return state

session = _Session()

# Set default sessions
Scheduler.session = session
Task.session = session
BaseCondition.session = session