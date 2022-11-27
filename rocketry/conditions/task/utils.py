from redbird.oper import in_, between

from rocketry.core.condition import All, Any
from rocketry.args import Task, Session
from rocketry.core.condition import BaseCondition
from rocketry.core.condition.base import BaseComparable
from rocketry.core.time.utils import get_period_span
from rocketry.pybox.time import to_timestamp
from rocketry.log.utils import get_field_value

class DependMixin(BaseCondition):

    _dep_actions = None

    def __init__(self, depend_task, task=None):
        self.task = task
        self.depend_task = depend_task
        super().__init__()

    @classmethod
    def _parse_multi_all(cls, depend_tasks:str, task=None):
        from rocketry.parse import ParserError
        tasks = depend_tasks.split("', '")
        if not tasks:
            raise ParserError
        return All(*(cls(depend_task=dep_task, task=task) for dep_task in tasks))

    @classmethod
    def _parse_multi_any(cls, depend_tasks:str, task=None):
        from rocketry.parse import ParserError
        tasks = depend_tasks.split("', '")
        if not tasks:
            raise ParserError
        return Any(*(cls(depend_task=dep_task, task=task) for dep_task in tasks))

    def get_state(self, task=Task(default=None), session=Session()):
        actual_task = session[self.task] if self.task is not None else task
        depend_task = session[self.depend_task]

        #! TODO: use Task._last_success & Task._last_run if not none and not forced
        last_depend_finish = depend_task.logger.get_latest(action=in_(self._dep_actions))
        last_actual_start = actual_task.logger.get_latest(action="run")

        if not last_depend_finish:
            # Depend has not run at all
            return False
        if not last_actual_start:
            # Depend has succeeded but the actual task has not
            return True

        return get_field_value(last_depend_finish, "created") > get_field_value(last_actual_start, "created")

class TaskStatusMixin(BaseComparable):

    _action = None

    def __init__(self, period=None, task=None):
        self.task = task
        self.period = period
        super().__init__()

    def get_measurement(self, task=Task(default=None), session=Session()):
        task = session[self.task] if self.task is not None else task
        _start_, _end_ = get_period_span(self.period if self.period is not None else task.period, session=session)

        allow_optimization = not self.session.config.force_status_from_logs

        if allow_optimization:

            # Get features that could be used to bypass reading logs
            if isinstance(self._action, str):
                last_occur = getattr(task, f'last_{self._action}')
                occurred_on_period = _start_ <= last_occur <= _end_ if last_occur is not None else False
                cannot_have_occurred = last_occur is None or last_occur < _start_
            else:
                # Multiple actions
                cannot_have_occurred = True
                for action in self._action:
                    last_occur = getattr(task, f'last_{action}')
                    if last_occur is not None and _start_ <= last_occur <= _end_:
                        occurred_on_period = True
                        cannot_have_occurred = False
                        break
                    if last_occur is not None and last_occur >= _start_:
                        cannot_have_occurred = False
                else:
                    occurred_on_period = False

            # Check if can be determined without reading logs
            # NOTE: if the last_occurred > _end_, we cannot determine whether the cond is true or not
            if self._is_equal_zero():
                if cannot_have_occurred:
                    return True
                if occurred_on_period:
                    return False
            if self._is_any_over_zero():
                if cannot_have_occurred:
                    # If never occurred, it hasn't occurred on the period either
                    return False
                if occurred_on_period:
                    return True


        records = task.logger.get_records(
            created=between(to_timestamp(_start_), to_timestamp(_end_)),
            action=in_(self._action) if isinstance(self._action, list) else self._action
        )
        return [
            get_field_value(record, "created")
            for record in records
        ]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        return f"task 'task '{task}' {self._action} {period}"
