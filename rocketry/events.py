from abc import abstractmethod, ABC
import datetime
import time
from typing import Any, Dict, List, Optional, Set
import inspect

from pydantic import BaseModel, Field

from rocketry.args import Task as TaskArg
from rocketry.conditions import BaseCondition
from rocketry.core import BaseArgument, Task
from rocketry.conds import new_scheduler_cycle

class BaseEvent(ABC, BaseModel):
    id: Optional[str]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    value: Any = None
    
    def __init__(self, value, **kwargs):
        super().__init__(value=value, **kwargs)

    @abstractmethod
    def consume(self, task):
        ...

    @abstractmethod
    def triggered(self, task) -> bool:
        ...

    def inactive(self, position:int, stream:'EventStream'):
        return False

class Batch(BaseEvent):
    "Consumable event"
    consumed: bool = False

    def consume(self, task):
        self.consumed = True

    def triggered(self, task):
        return not self.consumed

    def inactive(self, position:int, stream:'EventStream'):
        return self.consumed

class Event(BaseEvent):
    "Basic event"

    def consume(self, task):
        ...

    def triggered(self, task):
        last_run = task.get_last_run()
        in_future = self.timestamp > datetime.datetime.now()
        if in_future:
            # Future events won't trigger task
            return False
        if not last_run:
            # Haven't run previously
            return True
        return last_run < self.timestamp

    def inactive(self, position:int, stream:'EventStream'):
        return stream.event_stack[-1] is not self

class Trigger(BaseEvent):
    "Event that is true when a task hasn't processed it"
    processed_by: Set[Task] = Field(default_factory=set)

    def consume(self, task):
        self.processed_by.add(task)

    def triggered(self, task):
        return task not in self.processed_by


class EventStream(BaseCondition, BaseArgument):
    """
    
    Logic:
        1. Get items returned by the function
        2. 
    """
    event_stack: List[BaseEvent]

    def __init__(self, check_cond:BaseCondition=None, model:BaseEvent=Event, timeout=None):
        # How:
        # - Delete previous, add new (maintain consumed)
        # - Accumulate everything (can delete consumed)
        # Cases:
        # - Daily batches: report_date as value, no duplicates 
        if check_cond is None:
            check_cond = new_scheduler_cycle()
        self.check_cond = check_cond
        self.model = model
        self.timeout = timeout
        self._last_check = None
        self.event_stack = []
        self._processed_ids = set()

    def decorate(self, func):
        self.func = func
        return self

    def observe(self, task=TaskArg()):
        item = self.get_next(task=task)
        return item is not None

    def get_value(self, task=TaskArg(), **kwargs):
        item = self.get_next(task=task, **kwargs)
        if item:
            if task is not None:
                item.consume(task)
                if item.id is not None:
                    self._processed_ids.add(item.id)
            return item.value

    def get_next(self, task, **kwargs):
        items = self._get_items(task=task, **kwargs)
        for item in items:
            is_triggered = item.triggered(task) and item.id not in self._processed_ids
            if is_triggered:
                return item

    def _get_items(self, **kwargs) -> List[BaseEvent]:
        check_event = self.check_cond.observe(reference=0 if self._last_check is None else self._last_check, **kwargs)
        if check_event:

            if inspect.isgeneratorfunction(self.func):
                items = self.func()
            else:
                items = [self.func()]
            for item in items:
                if item is not None:
                    item = self._parse_event(item)
                    # TODO: This is run multiple times, same items are appended several times
                    # TODO: Check if item.id in item stack
                    self.event_stack.append(item)
            # Remove timeouted
            self.event_stack = [
                item
                for i, item in enumerate(self.event_stack)
                if not item.inactive(position=i, stream=self)
            ]
            self._last_check = time.time()
        return self.event_stack

    def _is_timeouted(self, item):
        if hasattr(item, "timestamp"):
            cutoff = datetime.datetime.now() - self.timeout
            if cutoff > item.timestamp:
                return True
        return False

    def _parse_event(self, event) -> BaseEvent:
        if isinstance(event, datetime.datetime):
            return self.model(timestamp=event, value=event)
        if isinstance(event, BaseEvent):
            return event
        return self.model(timestamp=datetime.datetime.now(), value=event)


def event_stream(*args, **kwargs):
    "Stream of events"
    return EventStream(*args, **kwargs).decorate

def batch_stream(*args, **kwargs):
    "Stream of batches"
    return EventStream(*args, model=Batch, **kwargs).decorate

def trigger_stream(*args, **kwargs):
    "Stream of triggers"
    return EventStream(*args, model=Trigger, **kwargs).decorate