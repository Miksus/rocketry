
from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles
from pypipe import reset
from pypipe.parameters import Parameters, ParameterSet

import pytest
import logging
import sys

def get_args():
    return 'positional 1', 'positional 2'

def get_kwargs():
    return {"x": "keyword x", "y": "keyword y"}

def get_args_kwargs():
    return ('positional 1', 'positional 2'), {"x": "keyword x", "y": "keyword y"}

def do_stuff_kwargs(*, x, y):
    assert x == 'keyword x'
    assert y == 'keyword y'

def do_stuff_args(arg1, arg2):
    assert arg1 == 'positional 1'
    assert arg2 == 'positional 2'

def do_stuff_args_kwargs(arg1, arg2, *, x, y):
    assert arg1 == 'positional 1'
    assert arg2 == 'positional 2'
    assert x == 'keyword x'
    assert y == 'keyword y'

def test_single_kwargs(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:

        task_get_kwargs = FuncTask(get_kwargs, name="get_kwargs")
        task_kwarg = FuncTask(do_stuff_kwargs, inputs=["get_kwargs"], dependent=["get_kwargs"])
        #task_arg = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_get_kwargs, task_kwarg,
            ], 
            shut_condition=scheduler_cycles >= 3,
            #parameters=Parameters(ParameterSet(x='keyword x', y='keyword y'))
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_kwarg.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()

