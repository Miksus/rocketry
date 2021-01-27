
from atlas.task.maintain import Refresher, ParamRefresher
import itertools

class SchedulerRefresher:
    def __init__(self, start_cond):
        self.start_cond = start_cond

    def __call__(self, task_strategies, maintainer_strategies, **kwargs):
        init_tasks = scheduler.tasks.copy()
        init_maintain = scheduler.maintainer_tasks.copy()
        refresh = Refresher(
            get_tasks=lambda: self._flatten_tasks(task_strategies) + init_tasks,
            get_maintainers=lambda: self._flatten_tasks(maintainer_strategies) + init_maintain,
            # Refresher starts when there is no task running
            start_cond=self.start_cond
        )
        refresh.force_state = True
        scheduler.maintainer_tasks = [refresh]
        scheduler.tasks = []

    def _flatten_tasks(self, funcs):
        materialized = map(lambda x: x(), funcs)
        return list(itertools.chain(*materialized))

