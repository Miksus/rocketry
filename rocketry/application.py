


import logging
from pathlib import Path
import tempfile
from typing import List, Optional, Pattern, Union
import warnings

from redbird import BaseRepo
from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo, CSVFileRepo
from rocketry.log.log_record import LogRecord

from rocketry.tasks import FuncTask, CommandTask
from rocketry.conditions import FuncCond
from rocketry.parameters import FuncParam
from rocketry import Session

class _AppMixin:
    
    session: Session

    def task(self, start_cond=None, name=None, **kwargs):
        """Create a task
        
        Parameters
        ----------
        start_cond : BaseCondition
            Starting condition of the task. When evaluates
            True, the task is set to run.
        name : str
            Name of the task. If not specified, the name
            is derived by the task class. For function
            tasks it is the name of the function.
        **kwargs
            Additional arguments passed to the task class.

        Examples
        --------
        .. codeblock::

            @app.task("daily")
            def get_value():
                return "Hello"
        """
        return self.session.create_task(start_cond=start_cond, name=name, **kwargs)

    def param(self, name:Optional[str]=None):
        """Create a parameter (from function)
        
        Parameters
        ----------
        name : str
            Name of the parameter.

        Examples
        --------
        .. codeblock::

            @app.param("my_value")
            def get_value():
                return "Hello"
        """
        return FuncParam(name, session=self.session)

    def cond(self, syntax: Union[str, Pattern, List[Union[str, Pattern]]]=None):
        """Create a custom condition (from function)
        
        Parameters
        ----------
        syntax : str, regex pattern, optional
            String expression for the condition. Used
            for condition language.

        Examples
        --------
        .. codeblock::

            @app.cond()
            def is_foo():
                return True or False

        """
        return FuncCond(syntax=syntax, session=self.session, decor_return_func=False)

    def params(self, **kwargs):
        "Set session parameters"
        self.session.parameters.update(kwargs)

    def include_grouper(self, group:'Grouper'):
        """Include contents of a grouper to the application"""
        for task in group.session.tasks:
            if group.prefix:
                task.name = group.prefix + task.name
            if group.start_cond is not None:
                task.start_cond = task.start_cond & group.start_cond
            task.execution = group.execution if task.execution is None else task.execution

            self.session.add_task(task)
        self.session.parameters.update(group.session.parameters)

class Rocketry(_AppMixin):
    """Rocketry scheduling application
    
    Parameters
    ----------
    session : Session, optional
        Scheduling session. Created if not passed.
    logger_repo: redbird.base.BaseRepo, optional
        Repository for the log records. MemoryRepo
        is created if not passed.
    **kwargs
        Keyword arguments passed to session creation.
    """

    def __init__(self, session:Session=None, logger_repo:Optional[BaseRepo]=None, execution=None, **kwargs):

        self.session = session if session is not None else Session(**kwargs)

        logger = logging.getLogger(self.session.config.task_logger_basename)
        logger.setLevel(logging.INFO)

        if execution is not None:
            self.session.config.task_execution = execution

        self._set_logger_with_repo(logger_repo)

    def run(self, debug=False):
        "Run the scheduler"
        self.session.config.debug = debug
        self.session.set_as_default()
        self.session.start()

    async def serve(self, debug=False):
        "Async run the scheduler"
        self.session.config.debug = debug
        self.session.set_as_default()
        await self.session.serve()

    def set_logger(self):
        warnings.warn((
            "set_logger is deprecated and will be removed in the future. " 
            "Please set the logger using logging.getLogger"
        ), DeprecationWarning)
        def wrapper(func):
            func(self._get_task_logger())
        return wrapper

    def _get_task_logger(self):
        logger_name = self.session.config.task_logger_basename
        return logging.getLogger(logger_name)

    def _set_logger_with_repo(self, repo):
        if isinstance(repo, str):
            self._get_repo(repo)
        elif repo is None:
            repo = MemoryRepo(model=LogRecord)
        logger = self._get_task_logger()
        logger.handlers.insert(0, RepoHandler(repo=repo))
    
    def _get_repo(self, repo:str):
        if repo == "memory":
            return MemoryRepo(model=LogRecord)
        elif repo == "csv":
            filepath = Path(tempfile.gettempdir()) / "rocketry.csv"
            return CSVFileRepo(filename=filepath, model=LogRecord)
        else:
            raise NotImplementedError(f"Repo creation for {repo} not implemented")

class Grouper(_AppMixin):
    """Task group
    
    This is a group of tasks (and other components)
    that can be added to an application later. Useful
    for bigger applications.

    Parameters
    ----------
    prefix : str, optional
        Prefix to add in front of the task names
        when including the grouper to an app.
    start_cond : BaseCondition, optional
        Condition that is added to every tasks' start
        condition in the group when including to an app.
        Every task in the group must fulfill this 
        condition as well to start.
    execution : str, optional
        Execution of the tasks in the group if not specified
        in the task. 
    """

    def __init__(self, prefix:str=None, start_cond=None, execution=None):
        self.prefix = prefix
        self.start_cond = start_cond
        self.execution = execution

        self.session = Session()
