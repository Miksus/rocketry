import datetime
import time
from typing import Any
from pydantic import BaseModel
from rocketry.args import Task
from rocketry.conditions import BaseCondition
from rocketry.core import BaseArgument
from rocketry.conds import true

class Event(BaseModel):
    datetime: datetime.datetime
    value: Any = None

class EventStream(BaseCondition, BaseArgument):

    def __init__(self, check_cond=None):
        if check_cond is None:
            check_cond = true
        self.check_cond = check_cond
        self._last_event = None
        self._last_check = None

    def decorate(self, func):
        self.func = func
        return self

    def observe(self, task=Task()):
        event = self._get_last_event(task=task)
        if event is None:
            return False
        event_time = event.datetime
        # Check if the event occurred after 
        # previous run of the task
        last_run = task.get_last_run()
        if last_run:
            return last_run < event_time
        else:
            return True

    def get_value(self, **kwargs):
        event = self._get_last_event(**kwargs)
        return event.value

    def _get_last_event(self, **kwargs) -> Event:
        check_event = self.check_cond.observe(reference=0 if self._last_check is None else self._last_check, **kwargs)
        if check_event:
            event = self.func()
            if event is None:
                event = None
            elif isinstance(event, datetime.datetime):
                event = Event(datetime=event, value=event)
            elif isinstance(event, Event):
                pass
            else:
                event = Event(datetime=datetime.datetime.now(), value=event)
            self._last_event = event
            self._last_check = time.time()
        return self._last_event

def event():
    "Event decorator"
    return EventStream().decorate