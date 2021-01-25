
from atlas.core.task import Task, clear_tasks, register_task_cls
from atlas.core.parameters import GLOBAL_PARAMETERS


@register_task_cls
class Refresher(Task):
    """Refresh the tasks and maintainer tasks of a scheduler
    by getting them via specified functions.
    """

    def __init__(self, get_tasks=None, get_maintainers=None, get_params=None, clear=True, **kwargs):
        super().__init__(**kwargs)
        self.clear = clear

        self.get_tasks = get_tasks
        self.get_maintainers = get_maintainers
        self.get_params = get_params

    def execute_action(self, _scheduler_, **kwargs):
        "Update tasks in the _scheduler_"
        if self.clear:
            clear_tasks(exclude=[self.name])

        _scheduler_.tasks = self.get_tasks()
        _scheduler_.maintainer_tasks = self.get_maintainers()

        if self.get_params is not None:
            _scheduler_.parameters.update(self.get_params())

    def get_default_name(self):
        return "task_refresher"

@register_task_cls
class ParamRefresher(Task):
    """Refresh scheduler's/session's/tasks' parameters with a function/callable 

    Args:
        Task ([type]): [description]
    """
    def __init__(self, get_params, clear=True, session=True, scheduler=False, tasks=None, **kwargs):
        super().__init__(**kwargs)
        self.get_params = get_params
        self.clear = clear
        self.session = session
        self.scheduler = scheduler
        self.tasks = tasks

    def execute_action(self, _scheduler_, **kwargs):
        params = self.get_params()

        param_sets = []
        if self.scheduler:
            param_sets.append(_scheduler_.parameters)
        if self.session:
            param_sets.append(GLOBAL_PARAMETERS)
        if self.tasks:
            for task in self.tasks:
                param_sets.append(get_task(task).parameters)

        for param_set in param_sets:
            if self.clear:
                param_set.clear()
            param_set.update(params)

    def get_default_name(self):
        return "param_refresher"