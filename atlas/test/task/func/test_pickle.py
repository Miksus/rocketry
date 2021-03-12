
from atlas import session
from atlas.task import FuncTask
from atlas.core import Parameters, Scheduler
from atlas.conditions import TaskFailed

import pickle

import pytest

def run_successful_func():
    print("Running func")

def test_func(tmpdir):
    # Process tasks must be picklable
    # in order to be run
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_successful_func, 
            name="example",
            execution="process"
        )
        # This should not return error
        pickle.dumps(task)

def test_lambda(tmpdir):
    # Lambda funcs cannot be pickled
    # thus this documents how that 
    # should fail
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None, 
            name="example",
            execution="process"
        )

        with pytest.raises(AttributeError, match=r".+[.]<locals>[.]<lambda>"):
            pickle.dumps(task)

def test_with_dependency(tmpdir):
    """A task must be pickleable even if
    it's depencency in start/end condition is not
    """
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        dep_task = FuncTask(lambda: None, name="Lambda func")

        task = FuncTask(
            run_successful_func, 
            name="example",
            execution="process",
            start_cond=TaskFailed(dep_task),
            end_cond=TaskFailed(dep_task),
        )
        # This should not return error
        pickle.dumps(task)