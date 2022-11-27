from typing import Dict, List, Callable, Tuple
import inspect

class _Hooker:
    # No, this is not what you think.

    def __init__(self, hooks:List[Callable], args:Tuple=None, kwargs:Dict=None):
        self.args = () if args is None else args
        self.kwargs = {} if kwargs is None else kwargs
        self.hooks = hooks

    def prerun(self, *args, **kwargs):
        from rocketry.core import Parameters
        self._post_hooks = []
        for hook in self.hooks:
            kwds = Parameters._from_signature(hook).materialize(**kwargs)
            result = hook(*args, **kwds)
            if inspect.isgeneratorfunction(hook):
                gener = result
                next(gener, None) # Executes first yield
                self._post_hooks.append(gener)

    def postrun(self, *args):
        for gener in self._post_hooks:
            try:
                gener.send(args)
            except StopIteration:
                pass

def clear_hooks():
    "Remove all hooks."
    from rocketry.core import Task, Scheduler
    Task.init_hooks = []
    Scheduler.startup_hooks = []
    Scheduler.cycle_hooks = []
    Scheduler.shutdown_hooks = []
