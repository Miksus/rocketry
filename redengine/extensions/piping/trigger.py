
import datetime
import time
from typing import Tuple, Union

import pandas as pd

from redengine.core import BaseCondition, Task
from redengine.conditions import Any, All, AlwaysFalse


class TriggerCluster(Any):
    
    def __init__(self, *triggers, task):
        self.subconditions = list(triggers)
        self.task = task
        self._last_check = (None, None, None)
    
    def __bool__(self):
        triggers = self.subconditions
        for trigger in triggers:
            if bool(trigger):
                return True
        return False

    def delete_trigger(self, trigger):
        self.subconditions = [
            trig
            for trig in self.subconditions
            if trig is not trigger
        ]

    @classmethod
    def find(cls, cond:BaseCondition):
        "Find existing TriggerCluster from given condition"
        if isinstance(cond, cls):
            return cond
        elif isinstance(cond, (Any, All)):
            for subcond in cond:
                if isinstance(subcond, TriggerCluster):
                    return subcond
        return None


class BaseTrigger(BaseCondition):

    _mark_trigger: datetime.datetime # Task run that has been attributed to this trigger

    def __init__(self, task, parent, depend_trigger:'BaseTrigger'):
        self.task = task
        self.parent = parent
        self.depend_trigger = depend_trigger

    def __bool__(self):
        return not self.has_running() and self.is_active() # not self.is_triggered() and 

    def is_first(self):
        "Check if the trigger is first of the pipe/sequence"
        return self.parent.triggers[0] is self

    def is_last(self):
        return self.parent.triggers[-1] is self

    def has_running(self):
        "Whether the TriggerCluster has any task running"
        cluster = self.parent
        for trigger in cluster.triggers:
            if trigger.task.is_running:
                return True
        return False

    def is_line_ordered(self) -> bool:
        """Whether the all the tasks before
        this trigger in the line (sequence/pipe)
        have run in order. Does not include 
        self's trigger's task

        Example:
        --------
            Examples of ine is in order:

                Normal:
                t0.task.last_run < self.task.last_run
                t0.task.last_run < self.task.last_run < t2.task.last_run
            
                What comes after won't matter 
                t0.task.last_run < self.task.last_run > t2.task.last_run
        """
        # TODO! Check if new session has started (parent.triggers[0].last_run > parent.get_last_run().task.last_run)
        if self.is_first():
            return True
        triggers = self.parent.triggers
        # Find the loc of current trigger (similar to index but it uses "==" instead of "is")
        for nth, trigger in enumerate(triggers):
            if self is trigger:
                break
        triggers_before_self = triggers[:nth]

        # Check the prev has run
        prev_trigger = triggers_before_self[-1]
        if prev_trigger.task.last_run is None:
            return False

        return self.runs_ordered(*triggers_before_self)

    def has_line_fails(self):
        triggers = self.parent.triggers
        line_start = triggers[0].task.last_run or datetime.datetime.min
        nth = triggers.index(self)
        for trigger in triggers[:nth]:
            if trigger.task.last_fail is not None and trigger.task.last_fail > line_start:
                return True
        return False

    @staticmethod
    def runs_ordered(*args: Tuple[Union[Task, 'BaseTrigger']]):
        """Check all the tasks have run in order 
        (former task in the tuple before latter in the tuple)

        Example:
        --------
            t0 > t1 > t2 > t3
            where t(n) is last_run of task n
        """
        pre_task = args[0] if isinstance(args[0], Task) else args[0].task
        for obj in args[1:]:
            task = obj if isinstance(obj, Task) else obj.task
            if pre_task.last_run is None and task.last_run is None:
                # NOT OK (if all the subsequent tasks also have last_run as None)
                return False
            elif pre_task.last_run is not None and task.last_run is None:
                # OK (if this is the last one)
                pass
            elif pre_task.last_run < task.last_run:
                # OK, current has run more recently
                pass
            else:
                return False
            pre_task = task
        return True

    @property
    def line_start(self):
        triggers = self.parent.triggers
        return triggers[0].task.last_run

    def delete(self):
        #! TODO
        cluster = TriggerCluster.find(self.task.start_cond)
        cluster.delete_trigger(self)

class IntervalTrigger(BaseTrigger):
    """
    Trigger that care about interval
    """

    def __init__(self, *args, **kwargs):
        # self.interval = interval
        super().__init__(*args, **kwargs)
        self._triggered_interval = pd.Interval(pd.Timestamp.min, pd.Timestamp.min)

    def is_active(self):
        last_run = self.task.last_run or datetime.datetime.min
        now = datetime.datetime.fromtimestamp(time.time())
        return (
            now in self.interval # It's time for the interval
            and last_run not in self.interval.rollback(now) # Has not run in the interval yet
            and self.is_line_ordered() # all the tasks before this have run one after another
            and not self.has_line_fails() # all the tasks before have not failed after start of the line
            and ((not self.is_first() and self.has_line_started()) or self.is_first())
        )

    def has_line_started(self):
        now = datetime.datetime.fromtimestamp(time.time())
        triggers = self.parent.triggers
        line_start = triggers[0].task.last_run or datetime.datetime.min
        return line_start in self.interval.rollback(now)

    def is_depend_ready(self):
        # TODO: Possibly merge this with active (remove this)
        is_first = self.is_first()
        if not is_first:
            depend_trigger = self.depend_trigger
            interval = depend_trigger.interval
            last_success = depend_trigger.task.last_success
            if last_success is None:
                # Has never succeeded (yet)
                return False
            now = datetime.datetime.fromtimestamp(time.time())
            return last_success in interval.rollback(now)
        elif is_first:
            return True

    def is_ready(self):
        "Whether the trigger has completed"
        interval = self.interval
        last_success = self.task.last_success
        if last_success is None:
            # Has never succeeded (yet)
            return False
        now = datetime.datetime.fromtimestamp(time.time())
        return last_success in interval.rollback(now)

    @property
    def interval(self):
        return self.parent.interval


class PulseTrigger(BaseTrigger):

    """Trigger that cares only if the dependend has
    succeeded.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._triggered_time = None

    def is_active(self):
        last_success = self.task.last_success
        depend_last_success = self.depend_trigger.task.last_success
        depend_last_fail = self.depend_trigger.task.last_fail

        if self.is_first():
            depend_trigger = self.parent.get_last_run()
            if self.task.last_run is None:
                return True
            elif not self.runs_ordered(self.task, depend_trigger.task):
                return False
            return (
                # Last one finished (fail or success) --> start new sequence
                depend_trigger.is_last() and (depend_trigger.task.status == "fail" or depend_trigger.task.status == "success")
            ) or (
                # The sequence failed somewhere in between --> start new sequence
                not depend_trigger.is_last() and depend_trigger.task.status == "fail"
            )
        else:
            depend_trigger = self.depend_trigger
            last_run = self.task.last_run or datetime.datetime.min
            depend_last_success = depend_trigger.task.last_success or datetime.datetime.min
            return depend_last_success > last_run
