from typing import List, Optional, Union

from pydantic import BaseModel

from rocketry.conditions import Any, All, DependFinish, DependSuccess
from rocketry.conditions.task import DependFailure
from rocketry.core import Task

from rocketry import Session

class Link:

    def __init__(self,
                 parent: Task,
                 child: Task,
                 relation: Optional[Union[DependSuccess, DependFailure, DependFinish]]=None,
                 type: Optional[Union[Any, All]]=None):
        self.parent = parent
        self.child = child
        self.relation = relation
        self.type = type

    def __iter__(self):
        return iter((self.parent, self.child))

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return (
                self.parent == other.parent
                and self.child == other.child
                and self.relation == other.relation
                and self.type == other.type
            )
        return False

    def __str__(self):
        s = f'{self.parent.name!r} -> {self.child.name!r}'
        if self.type is All:
            s += ' (multi)'
        return s

    def __repr__(self):
        return f'Link({self.parent.name!r}, {self.child.name!r}, relation={getattr(self.relation, "__name__", None)}, type={getattr(self.type, "__name__", None)})'

class Dependencies(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    session: Session

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)

    def __iter__(self):
        for task in self.session.tasks:
            yield from self._get_links(task)

    def _get_links(self, task:Task) -> Union[Any, All]:
        cond = task.start_cond
        if isinstance(cond, (Any, All)):
            for subcond in cond:
                if isinstance(subcond, (DependFinish, DependSuccess, DependFailure)):
                    req_task = subcond.depend_task
                    req_task = self.session[req_task]
                    yield Link(parent=req_task, child=task, relation=type(subcond), type=type(cond))
        elif isinstance(cond, (DependFinish, DependSuccess, DependFailure)):
            req_task = cond.depend_task
            req_task = self.session[req_task]
            yield Link(req_task, task, relation=type(cond))


def get_dependencies(session) -> List[Link]:
    "Get list of dependency links"
    return list(Dependencies(session))
