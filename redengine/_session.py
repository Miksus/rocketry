

"""
Utilities for getting information 
about the scehuler/task/parameters etc.
"""

import logging
from pathlib import Path
from redengine.pybox.io.read import read_yaml
from typing import Iterable, Dict, List, Type, Union
from itertools import chain

import redengine
from redengine.core import BaseExtension, extensions, parameters
from redengine.core.log import TaskAdapter
from redengine.core import Scheduler, Task, BaseCondition, Parameters, BaseArgument
from redengine.conditions import Any
from redengine.config import get_default, DEFAULT_BASENAME_TASKS, DEFAULT_BASENAME_SCHEDULER
from redengine import parse

class Session:
    """Collection of the scheduler objects.

    Parameters
    ----------

    config : dict, optional
        Central configuration for defining behaviour
        of different object and classes in the session.
    tasks : Dict[str, redengine.core.Task], optional
        Tasks of the session. Can be formed later.
    parameters : parameter-like, optional
        Session level parameters.
    extensions: dict, optional
        Extensions of the session. Can be formed later.
    scheme : str or list, optional
        Premade scheme(s) to use to set up logging, 
        parameters, setup tasks etc.
    as_default : bool, default=True
        Whether to set the session as default for next
        tasks, extensions etc. that don't have session
        specified.
    kwds_scheduler : dict, optional
        Keyword arguments passed to 
        :py:class:`redengine.core.Scheduler`.
    delete_existing_loggers : bool, default=False
        If True, deletes the loggers that already existed
        for the task logger basename.

    Attributes
    ----------
    config : dict
        Central configuration for defining behaviour
        of different object and classes in the session.
    scheduler : Scheduler
        Scheduler of the session.
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

    parser = parse.StaticParser({
            "logging": parse.Field(parse.parse_logging, if_missing="ignore"),
            "parameters": parse.Field(parse.parse_session_params, if_missing="ignore", types=(dict,)),
            "tasks": parse.Field(parse.parse_tasks, if_missing="ignore", types=(dict, list)),
            "scheduler": parse.Field(parse.parse_scheduler, if_missing="ignore"),
            # Note that extensions are set in redengine.ext
        },
        on_extra="ignore", 
    )

    def __init__(self, 
                 config:dict=None, 
                 tasks:dict=None, 
                 parameters:Parameters=None, 
                 extensions:dict=None, 
                 scheme:Union[str,list]=None, 
                 as_default=True,
                 kwds_scheduler=None, 
                 delete_existing_loggers=False):
        # Set defaults
        config = {} if config is None else config
        
        extensions = {} if extensions is None else extensions

        # Set attrs
        self.config = self.default_config.copy()
        self.config.update(config)

        self.tasks = tasks
        self.returns = Parameters()
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
        if as_default:
            self.set_as_default()

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
        get_default(scheme, scheduler_basename=scheduler_basename, task_basename=task_basename, session=self)

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
            Placeholders and loggers built for parallelized
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
        """Delete the previous loggers from task logger"""
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
        state["_tasks"] = None
        state["_extensions"] = None
        state["scheduler"] = None
        state["parser"] = None
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

    @property
    def tasks(self) -> Dict[str, Task]:
        """Dict[str, Task]: Dictionary of the tasks in the session.
        The key is the name of the task and values are the 
        :py:class:`redengine.core.Task` objects."""
        return self._tasks

    @tasks.setter
    def tasks(self, item:Union[List[Task], Dict[str, Task]]):
        tasks = {}
        if item is None:
            pass
        elif isinstance(item, (list, tuple, set)):
            for task in item:
                if not isinstance(task, Task):
                    raise TypeError(f"Session tasks must be type {Task}. Given: {type(task)}")
                tasks[task.name] = task
        elif isinstance(item, dict):
            tasks = item
            #! TODO: Validate
        else:
            raise TypeError(f"Tasks must be either list or dict. Given: {type(item)}")
        self._tasks = tasks

    @property
    def parameters(self) -> Parameters:
        """Parameters: Session level parameters."""
        return self._params

    @parameters.setter
    def parameters(self, item:Union[Dict, Parameters]):
        self._params = Parameters(item)

    @property
    def extensions(self) -> Dict[str, Dict[str, BaseExtension]]:
        """Dict[str, Dict[str, BaseExtension]]: Dictionary of the extensions 
        in the session. The first key is the parse keys of the extensions
        and second key the names of the extension objects."""
        return self._extensions

    @extensions.setter
    def extensions(self, item:Union[List[BaseExtension], Dict[str, Dict[str, BaseExtension]]]):
        exts = {}
        if item is None:
            pass
        elif isinstance(item, list):
            for ext in item:
                if not isinstance(ext, BaseExtension):
                    raise TypeError(f"Session extensions must be type {BaseExtension}. Given: {type(ext)}")
                key = ext.__parsekey__
                if key not in exts:
                    exts[key] = {}
                exts[key][ext.name] = ext
        elif isinstance(item, dict):
            exts = item
            #! TODO: Validate
        else:
            raise TypeError(f"Extensions must be either list or dict. Given: {type(item)}")
        self._extensions = exts

    @classmethod
    def from_yaml(cls, file:Union[str, Path], **kwargs) -> 'Session':
        """Create session from a YAML file.

        Parameters
        ----------
        file : path-like
            YAML configuration file path.
        **kwargs : dict
            Passed to Session.from_dict.
        """
        d = read_yaml(file)
        d = {} if d is None else d
        return cls.from_dict(d, **kwargs)

    @classmethod
    def from_dict(cls, conf:dict, root=None, session:'Session'=None, kwds_fields:dict=None, **kwargs) -> 'Session':
        """Create session from a dictionary.

        There are some extra options or functionalities to help 
        with the creation of the tasks:

        - The task class is read from the key ``conf['tasks'][...]['class']``.
          See ``redengine.core.task.CLS_TASKS`` for list of classes.
        - For some tasks that lack specified classes the class is determined
          from the arguments:
        - If argument ``path`` has suffix ``.py``, the class is ``FuncTask``.

        Parameters
        ----------
        conf : dict
            Dict to turn to session.
        root : path-like, optional
            If passed, tasks that have ``path`` in their init
            arguments have this argument modified. The ``root``
            will be set as the parent directory for the path 
            if ``path`` is relative. Useful to make the session
            to work the same regardless of current working 
            directory.
        session : Session, optional
            If provided, this session is appended with the parsed
            content instead of creating a new one.
        kwds_fields: dict, optional
            Additional keyword arguments passed to the subparsers.
            For example, the values of key 'task' are passed to
            redengine.parse.parse_tasks.
        **kwargs : dict
            Additional parameters passed to all subparsers.
        """
        session = cls() if session is None else session
        kwds_fields = {} if kwds_fields is None else kwds_fields
        if root is not None:
            if "tasks" not in kwds_fields:
                kwds_fields["tasks"] = {}
            kwds_fields["tasks"] = {"kwds_subparser": {"root": root}}
        cls.parser(conf, session=session, kwds_fields=kwds_fields, **kwargs)
        return session