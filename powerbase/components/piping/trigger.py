
import datetime
from powerbase.core.task.base import Task
from typing import Tuple, Union
from powerbase.components.base import BaseComponent
from powerbase.core import BaseCondition
from powerbase.conditions import Any, All, AlwaysFalse
from powerbase.parse import parse_time, parse_task

import pandas as pd

class TriggerCluster(Any):
    
    def __init__(self, *triggers, task):
        self.subconditions = list(triggers)
        self.task = task
        self._last_check = (None, None, None)
        self._queue = []
    
    def __bool__(self):

        has_changed = self.has_changed()
        if has_changed:
            self.trigger()
            self.change()

        triggers = self.subconditions
        for trigger in triggers:
            if bool(trigger):
                if has_changed:
                    # Pretrigger, the trigger should be triggered
                    # when something changes next time
                    self.add_queue(trigger)
                return True
        return False

    def has_changed(self):
        """Whether the status of the task has changed 
        or not."""
        last_run = self.task.last_run
        last_success = self.task.last_success
        last_fail = self.task.last_fail
        return self._last_check != (last_run, last_fail, last_success)

    def change(self):
        last_run = self.task.last_run
        last_success = self.task.last_success
        last_fail = self.task.last_fail
        self._last_check = (last_run, last_fail, last_success)

    def trigger(self):
        "Trigger trigger(s)"

        # TODO: Some triggers trigger depending on what changed
        # trigger_on_succes, trigger_on_run, trigger_on_fail
        # Also need to make sure the new run/success/fail happened
        # on the trigger's interval (otherwise should not be triggered) (Hmm, maybe the new logic handles this)

        last_run = self.task.last_run
        if self._queue:
            trigger = self._queue.pop(0)
        else:
            trigger = next(iter(self.triggers))
        
        trigger.trigger()
        
    def trigger(self):
        "Trigger trigger(s)"

        # TODO: Some triggers trigger depending on what changed
        # trigger_on_succes, trigger_on_run, trigger_on_fail
        # Also need to make sure the new run/success/fail happened
        # on the trigger's interval (otherwise should not be triggered) (Hmm, maybe the new logic handles this)
        run_changed = self._last_check[0] != self.task.last_run
        success_changed = self._last_check[1] != self.task.last_success
        fail_changed = self._last_check[2] != self.task.last_fail

        if run_changed:
            for n, trigger in enumerate(self._queue):
                if trigger.trigger_on == "run":
                    trigger.trigger()
                    del self._queue[n]
                    break

        if success_changed:
            for n, trigger in enumerate(self._queue):
                if trigger.trigger_on == "success":
                    trigger.trigger()
                    del self._queue[n]
                    break
            
        if fail_changed:
            for n, trigger in enumerate(self._queue):
                if trigger.trigger_on == "fail":
                    trigger.trigger()
                    del self._queue[n]
                    break

    def add_queue(self, trigger):
        self._queue.append(trigger)


class BaseTrigger(BaseCondition):

    _mark_trigger: datetime.datetime # Task run that has been attributed to this trigger

    def __init__(self, task, parent, depend_trigger:'BaseTrigger'):
        self.task = task
        self.parent = parent
        self.depend_trigger = depend_trigger

    def __bool__(self):
        return not self.is_triggered() and not self.has_running() and self.is_active()

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
        now = datetime.datetime.now()
        return (
            now in self.interval # It's time for the interval
            and last_run not in self.interval.rollback(now) # Has not run in the interval yet
            and self.is_line_ordered() # all the tasks before this have run one after another
            and not self.has_line_fails() # all the tasks before have not failed after start of the line
            and ((not self.is_first() and self.has_line_started()) or self.is_first())
        )

    def is_triggered(self):
        "Whether the trigger has been marked to have fired (but not necessarily completed)"
        # TODO: If no interval, is_triggered should probably be: self.depend_trigger.task.last_success <= self._triggered_interval.start
        last_trigger_interval = self._triggered_interval
        curr_interval = self.interval.rollback(datetime.datetime.now())
        return curr_interval.left == last_trigger_interval.left

    def trigger(self, dt):
        "TriggerCluster should call this"
        self._triggered_interval = self.interval.rollback(dt).start

    def has_line_started(self):
        now = datetime.datetime.now()
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
            return last_success in interval.rollback(datetime.datetime.now())
        elif is_first:
            return True

    def is_ready(self):
        "Whether the trigger has completed"
        interval = self.interval
        last_success = self.task.last_success
        if last_success is None:
            # Has never succeeded (yet)
            return False
        return last_success in interval.rollback(datetime.datetime.now())

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

    def is_triggered(self):
        "Whether the trigger has been marked to have fired (but not necessarily completed)"
        last_trigger_interval = self._triggered_time
        if last_trigger_interval is None:
            return False
        last_run = self.task.last_run
        return last_trigger_interval == last_run

    def trigger(self, dt):
        "TriggerCluster should call this"
        self._triggered_time = dt


# OLD
class TriggerOld(BaseCondition):

    # TODO: The finishing of the trigger needs to be recorded
    # some way

    # TODO: new function: ready() -> bool
    # Determines whether the current trigger is 

    _mark_trigger: datetime.datetime # Task run that has been attributed to this trigger

    def __init__(self, task, parent, depend_trigger:'Trigger'):
        self.task = task
        self.parent = parent
        self.depend_trigger = depend_trigger
        self._triggered_interval = pd.Interval(pd.Timestamp.min, pd.Timestamp.min)

    def __bool__(self):
        # TODO: Remove is_depend_ready and merge with is_active
        return not self.is_triggered() and self.is_active() and self.is_depend_ready()

    def is_active(self):
        if self.has_interval():
            return datetime.datetime.now() in self.interval
        else:
            # Check current task has not succeeded after dependent
            return self.is_active_depend_ready()

    def _is_active_depend_ready_interval(self):
        pass

    def _is_active_depend_ready_no_interval(self):
        "True if depend task has succeeded and current has not"
        # TODO: If first logic
        last_success = self.task.last_success
        depend_last_success = self.depend_trigger.task.last_success
        depend_last_fail = self.depend_trigger.task.last_fail

        if self.is_first():
            depend_trigger = self.parent.get_last_run()

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

    def is_depend_ready(self):
        # TODO: Possibly merge this with active (remove this)
        is_first = self.is_first()
        has_interval = self.has_interval()
        if not has_interval:
            return True

        if not is_first:
            return self.depend_trigger.is_ready()
        elif is_first:
            return True

    def is_ready(self):
        "Whether the trigger has completed"
        interval = self.interval
        last_success = self.task.last_success
        if last_success is None:
            # Has never succeeded (yet)
            return False
        elif interval is None:
            # TODO! Not sure about this
            # Has no interval thus is ready only if
            # current has succeeded after dependent
            last_run = self.task.last_run
            last_fail = self.task.last_fail or datetime.datetime.min
            is_task_succeeded = last_run <= last_success and last_fail <= last_success
            
            if not is_task_succeeded:
                return False

            # Next we test the task has succeeded after previous success
            depend_trigger = self.depend_trigger
            if depend_trigger is None:
                # No previous task and current has succeeded
                # --> The trigger has completed
                return True

            is_prev_succeeded_before = (
                last_success >= self.depend_trigger.task.last_success 
                if self.depend_trigger.task.last_success is not None
                else False # Prev task has not succeeded yet but current has succeeded --> not completed
            )
            return is_prev_succeeded_before
        return last_success in interval.rollback(datetime.datetime.now())

    def is_triggered(self):
        "Whether the trigger has been marked to have fired (but not necessarily completed)"
        # TODO: If no interval, is_triggered should probably be: self.depend_trigger.task.last_success <= self._triggered_interval.start
        last_trigger_interval = self._triggered_interval
        curr_interval = self.interval.rollback(datetime.datetime.now())
        return curr_interval.start == last_trigger_interval.start

    def is_first(self):
        "Check if the trigger is first of the pipe/sequence"
        return self.parent.triggers[0] is self

    def is_last(self):
        return self.parent.triggers[-1] is self

    def is_success(self):
        "Latest run has succeeded"
        return self.task.status == "success"

    def has_interval(self):
        return self.interval is not None

    def trigger(self, dt):
        "TriggerCluster should call this"
        self._triggered_interval = self.interval.rollback(dt).start

    @property
    def interval(self):
        interval = self.parent.interval
        if interval:
            return interval
        else:
            return 
