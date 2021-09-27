

"""
Utilities for getting information 
about the scehuler/task/parameters etc.
"""

import logging
from redengine.conditions import Any
from redengine.core import BaseExtension
from typing import Iterable, List, Dict, Type, Union
from pathlib import Path
from itertools import chain
import pandas as pd

from redengine.core.log import TaskAdapter
from redengine.core import Scheduler, Task, BaseCondition, Parameters, BaseArgument
from redengine.core import condition

from redengine.log import CsvHandler, CsvFormatter
from redengine.config import get_default, DEFAULT_BASENAME_TASKS, DEFAULT_BASENAME_SCHEDULER
import redengine

class Session:
    """Collection of the scheduler objects.

    Attributes
    ----------
    tasks : dict
        Tasks the session has. These tasks are used for
        the scheduler. Keys of the dict are the names
        of the tasks. 
    config : dict
        Central configuration for defining behaviour
        of different object and classes in the session.
    parameters : Parameters
        Parameters feeded to the tasks.
    scheduler : Scheduler
        Scheduler of the session.
    extensions : dict
        External components that help to shape the 
        behaviour of tasks. These are built on top
        of the core functionalities and extends it.
        This is not much used by anything but 
        stored in the session if the user wants to 
        access them.
    delete_existing_loggers : bool
        If True, all loggers that match the 
        session.config['basename'] are deleted (by 
        default, deletes loggers starting with 
        'redengine.task').

    """

    tasks: Dict[str, Task]
    config: Dict[str, Any]
    extensions: Dict[Type, Dict[str, BaseExtension]]
    parameters: Parameters
    scheduler: Scheduler

    cls_scheduler = Scheduler

    default_config = {
        "use_instance_naming": False, # Whether to use id(task) as task.name if name not specified
        "task_pre_exist": "raise", # What to do if a task name is already taken
        "force_status_from_logs": False, # Force to check status from logs every time (slow but robust)
        "task_logger_basename": DEFAULT_BASENAME_TASKS,
        "scheduler_logger_basename": DEFAULT_BASENAME_SCHEDULER,

        #"session_store_cond_cls": True,
        #"session_store_task_cls": True,
        "debug": False,
    }

    def __init__(self, config:dict=None, tasks:dict=None, parameters:Parameters=None, extensions:dict=None, scheme:Union[str,list]=None, kwds_scheduler=None, delete_existing_loggers=False):
        # Set defaults
        config = {} if config is None else config
        tasks = {} if tasks is None else tasks
        parameters = (
            Parameters() if parameters is None 
            else Parameters(parameters) if not isinstance(parameters, Parameters)
            else parameters
        )
        extensions = {} if extensions is None else extensions

        # Set attrs
        self.config = self.default_config.copy()
        self.config.update(config)

        self.tasks = tasks
        self.parameters = parameters
        self.extensions = extensions

        if delete_existing_loggers:
            # Delete existing task loggers
            # so that the old loggers won't
            # interfere with the ones created 
            # with schemes.
            self.delete_task_loggers()

        kwds_scheduler = {} if kwds_scheduler is None else kwds_scheduler
        self.scheduler = self.cls_scheduler(session=self, **kwds_scheduler)
        if scheme is not None:
            is_list_of_schemes = not isinstance(scheme, str)
            if is_list_of_schemes:
                for sch in scheme:
                    self.set_scheme(sch)
            else:
                self.set_scheme(scheme)

    def set_scheme(self, scheme:str):
        """Set logging/scheduling scheme from
        default schemes.

        Parameters
        ----------
        scheme : str
            Name of the scheme. See redengine.config.defaults
        """
        #! TODO: A function to list existing defaults and help of them
        scheduler_basename = self.config["scheduler_logger_basename"]
        task_basename = self.config["task_logger_basename"]
        get_default(scheme, scheduler_basename=scheduler_basename, task_basename=task_basename)

    def start(self):
        """Start the scheduling session.

        Will block and wait till the scheduler finishes 
        if there is a shut condition."""
        self.scheduler()

    def get_tasks(self) -> list:
        """Get session tasks as list.

        Returns
        -------
        list[Task]
            List of tasks in the session.
        """
        return self.tasks.values()

    def get_task(self, task):
        #! TODO: Do we need this?
        return self.tasks[task] if not isinstance(task, Task) else task

    def get_task_loggers(self, with_adapters=True) -> Dict[str, Union[TaskAdapter, logging.Logger]]:
        """Get task logger(s) from the session.

        Parameters
        ----------
        with_adapters : bool, optional
            Whether get the loggers wrapped to 
            redengine.core.log.TaskAdapter, by default True

        Returns
        -------
        Dict[str, Union[TaskAdapter, logging.Logger]]
            Dictionary of the loggers (or adapters)
            in which the key is the logger name.
            Placeholders and loggers built for parallerized
            tasks are ignored.
        """

        basename = self.config["task_logger_basename"]
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger 
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith(basename) 
            and not isinstance(logger, logging.PlaceHolder)
            and not name.endswith("_process") # No private
        }

    def get_scheduler_loggers(self, with_adapters=True) -> Dict[str, Union[TaskAdapter, logging.Logger]]:
        """Get scheduler logger(s) from the session.

        Parameters
        ----------
        with_adapters : bool, optional
            Whether get the loggers wrapped to 
            redengine.core.log.TaskAdapter, by default True

        Returns
        -------
        Dict[str, Union[TaskAdapter, logging.Logger]]
            Dictionary of the loggers (or adapters)
            in which the key is the logger name.
            Placeholders and private loggers are ignored.
        """
        basename = self.config["scheduler_logger_basename"]
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger  
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith(basename) 
            and not isinstance(logger, logging.PlaceHolder)
            and not name.startswith("_") # No private
        }

# Log data
    def get_task_log(self, **kwargs) -> Iterable[Dict]:
        """Get task log records from all of the 
        readable handlers in the session.

        Parameters
        ----------
        **kwargs : dict
            Query parameters passed to 
            redengine.core.log.TaskAdapter.get_records

        Returns
        -------
        Iterable[Dict]
            Generator of the task log records.
        """
        loggers = self.get_task_loggers(with_adapters=True)
        data = iter(())
        for logger in loggers.values():
            data = chain(data, logger.get_records(**kwargs))
        return data

    def get_scheduler_log(self, **kwargs) -> Iterable[Dict]:
        """Get scheduler log records from all of the 
        readable handlers in the session.

        Parameters
        ----------
        **kwargs : dict
            Query parameters passed to 
            redengine.core.log.TaskAdapter.get_records

        Returns
        -------
        Iterable[Dict]
            Generator of the task log records.
        """
        loggers = self.get_scheduler_loggers(with_adapters=True)
        data = iter(())
        for logger in loggers.values():
            data = chain(data, logger.get_records(**kwargs))
        return data
        
    def delete_task_loggers(self):
        "Delete the "
        loggers = logging.Logger.manager.loggerDict
        for name in list(loggers):
            if name.startswith(self.config["task_logger_basename"]):
                del loggers[name]

    def clear(self):
        """Clear tasks, parameters etc. of the session"""
        #! TODO: Remove?
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

    @property
    def env(self):
        "Shorthand for parameter 'env'"
        return self.parameters.get("env")

    @env.setter
    def env(self, value):
        "Shorthand for parameter 'env'"
        self.parameters["env"] = value

    def set_as_default(self):
        """Set this session as the default session for 
        next tasks, conditions and schedulers that
        are created.
        """
        Scheduler.session = self
        Task.session = self
        BaseCondition.session = self
        Parameters.session = self
        BaseExtension.session = self
        redengine.session = self
        BaseArgument.session = self