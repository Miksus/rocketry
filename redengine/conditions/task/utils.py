
from redengine.core.condition import All, Any

class DependMixin:

    _dep_actions = None

    def __init__(self, depend_task, task=None, **kwargs):
        super().__init__(task=task, depend_task=depend_task, **kwargs)

    @classmethod
    def _parse_multi_all(cls, depend_tasks:str, task=None):
        from redengine.parse import ParserError
        tasks = depend_tasks.split("', '")
        if not tasks:
            raise ParserError
        return All(*(cls(depend_task=dep_task, task=task) for dep_task in tasks))

    @classmethod
    def _parse_multi_any(cls, depend_tasks:str, task=None):
        from redengine.parse import ParserError
        tasks = depend_tasks.split("', '")
        if not tasks:
            raise ParserError
        return Any(*(cls(depend_task=dep_task, task=task) for dep_task in tasks))

    def observe(self, task, depend_task, **kwargs):
        """True when the "depend_task" has succeeded and "task" has not yet ran after it.
        Useful for start cond for task that should be run after success of another task.
        """
        actual_task = self.session.get_task(task)
        depend_task = self.session.get_task(depend_task)

        #! TODO: use Task._last_success & Task._last_run if not none and not forced
        last_depend_finish = depend_task.logger.get_latest(action=self._dep_actions)
        last_actual_start = actual_task.logger.get_latest(action=["run"])

        if not last_depend_finish:
            # Depend has not run at all
            return False
        elif not last_actual_start:
            # Depend has succeeded but the actual task has not
            return True
            
        return last_depend_finish["timestamp"] > last_actual_start["timestamp"]