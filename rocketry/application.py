import logging
from typing import List, Optional, Pattern, Union
import warnings

from redbird import BaseRepo
from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from rocketry.log.log_record import LogRecord

from rocketry.conditions import FuncCond
from rocketry.parameters import FuncParam
from rocketry import Session

class _AppMixin:

    session: Session

    def task(self, start_cond=None, name=None, **kwargs):
        "Create a task"
        return self.session.create_task(start_cond=start_cond, name=name, **kwargs)

    def param(self, name:Optional[str]=None):
        "Set one session parameter (decorator)"
        return FuncParam(name, session=self.session)

    def cond(self, syntax: Union[str, Pattern, List[Union[str, Pattern]]]=None):
        "Create a condition (decorator)"
        return FuncCond(syntax=syntax, session=self.session, decor_return_func=False)

    def params(self, **kwargs):
        "Set session parameters"
        self.session.parameters.update(kwargs)

    def include_grouper(self, group:'Grouper'):
        for task in group.session.tasks:
            if group.prefix:
                task.name = group.prefix + task.name
            if group.start_cond is not None:
                task.start_cond &= group.start_cond
            task.execution = group.execution if task.execution is None else task.execution

            self.session.add_task(task)
        self.session.parameters.update(group.session.parameters)

class Rocketry(_AppMixin):
    """Rocketry scheduling application"""

    def __init__(self, session:Session=None, logger_repo:Optional[BaseRepo]=None, **kwargs):

        self.session = session if session is not None else Session(**kwargs)

        logger = logging.getLogger(self.session.config.task_logger_basename)
        logger.setLevel(logging.INFO)

        self._set_logger_with_repo(logger_repo)

    def run(self, debug=False):
        "Run the scheduler"
        self.session.config.debug = debug
        self.session.set_as_default()
        self.session.start()

    async def serve(self, debug=False):
        "Run the scheduler"
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
        if repo is None:
            repo = MemoryRepo(model=LogRecord)
        logger = self._get_task_logger()
        logger.handlers.insert(0, RepoHandler(repo=repo))

    def setup(self, func=None):
        if func is not None:
            return self.session.hook_startup()(func)
        return self.session.hook_startup()

class Grouper(_AppMixin):

    def __init__(self, prefix:str=None, start_cond=None, execution=None):
        self.prefix = prefix
        self.start_cond = start_cond
        self.execution = execution

        # task_execution here should not matter
        self.session = Session(execution="async")
