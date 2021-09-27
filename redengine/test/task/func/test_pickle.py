
import pickle

import pytest

from redengine.tasks import FuncTask
from redengine.conditions import TaskFailed

def run_successful_func():
    print("Running func")

def test_func(tmpdir, session):
    # Process tasks must be picklable
    # in order to be run
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            run_successful_func, 
            name="example",
            execution="process"
        )
        # This should not return error
        pickle.dumps(task)

def test_lambda(tmpdir, session):
    # Lambda funcs cannot be pickled
    # thus this documents how that 
    # should fail
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            lambda : None, 
            name="example",
            execution="process"
        )

        with pytest.raises(AttributeError, match=r".+[.]<locals>[.]<lambda>"):
            pickle.dumps(task)

def test_with_dependency(tmpdir, session):
    """A task must be pickleable even if
    it's depencency in start/end condition is not
    """
    with tmpdir.as_cwd() as old_dir:

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
