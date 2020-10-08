

from pypipe import Scheduler, MultiScheduler, JupyterTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles, task_ran, scheduler_started
from pypipe.parameters import Parameters, ParameterSet
from pypipe import reset

from jubox import JupyterNotebook, CodeCell

import pytest
import logging
import sys
import time

import pandas as pd

def test_simple(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        
        nb = JupyterNotebook([
            CodeCell(""),
            CodeCell("x = 'keyword 1'\ny = 'keyword 2'", tags=["parameters"]),
            CodeCell("assert x == 'keyword 1'\nassert y == 'keyword 2'", tags=["parameters"]),
        ])
        nb.to_ipynb("example.ipynb")

        task = JupyterTask("example.ipynb", name="a_task")
        sched = MultiScheduler([
            task,
        ], shut_condition=task_ran(task="a_task") >= 3)
        sched()

        history = task.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_parametrized(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        
        nb = JupyterNotebook([
            CodeCell(""),
            CodeCell("x = 'wrong'\ny = 'wrong'", tags=["parameter"]),
            CodeCell("assert x == 'keyword 1'\nassert y == 'keyword 2'"),
        ])
        nb.to_ipynb("example.ipynb")

        task = JupyterTask("example.ipynb", name="a_task")
        sched = MultiScheduler([
            task,
        ], 
            shut_condition=task_ran("a_task") >= 3,
            parameters=Parameters(ParameterSet(x="keyword 1", y="keyword 2"))
        )
        sched()

        history = task.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()

def test_parametrized_pickled(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        
        nb = JupyterNotebook([
            CodeCell(""),
            CodeCell("x = 'wrong'\ny = 'wrong'", tags=["parameter"]),
            CodeCell("import pandas as pd"),
            CodeCell("assert isinstance(x, pd.Series)\nassert isinstance(y, pd.Series)"),
        ])
        nb.to_ipynb("example.ipynb")

        task = JupyterTask("example.ipynb", name="a_task")
        sched = MultiScheduler([
            task,
        ], 
            shut_condition=task_ran("a_task") >= 3,
            parameters=Parameters(ParameterSet(x=pd.Series({"a": [1,2,3]}), y=pd.Series({"b": [1,2,3]})))
        )
        sched()

        history = task.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()