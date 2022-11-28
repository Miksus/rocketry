import pickle
from inspect import isfunction

import pytest

from rocketry.tasks import FuncTask
from rocketry.conditions import TaskFailed
from rocketry.core import Parameters

def func_on_main_level():
    pass

def pickle_dump_read(obj):
    p = pickle.dumps(obj)
    return pickle.loads(p)

class TestFunc:

    def test_func_on_main(self, session):
        task = FuncTask(func_on_main_level, session=session)
        pick_task = pickle_dump_read(task)
        assert pick_task.func.__name__ == "func_on_main_level"
        assert isfunction(pick_task.func)

    def test_func_nested(self, session):
        # This cannot be pickled (cannot use execution == process)
        def func_nested():
            pass
        task = FuncTask(func_nested, execution="process", name="unpicklable", session=session)
        with pytest.raises(AttributeError):
            pickle_dump_read(task)
        # This should not raise (though still not pickleable)
        task = FuncTask(func_nested, execution="thread", name="picklable", session=session)

    def test_unpicklable_start_cond(self, session):
        def func_nested():
            pass
        unpkl_task = FuncTask(func_nested, execution="thread", session=session)
        task = FuncTask(func_on_main_level, execution="process", start_cond=TaskFailed(task=unpkl_task), session=session)

        pick_task = pickle_dump_read(task)
        assert pick_task.func.__name__ == "func_on_main_level"
        assert isfunction(pick_task.func)
        assert pick_task.start_cond is None

    def test_unpicklable_end_cond(self, session):
        def func_nested():
            pass
        unpkl_task = FuncTask(func_nested, execution="thread", session=session)
        task = FuncTask(func_on_main_level, execution="process", end_cond=TaskFailed(task=unpkl_task), session=session)

        pick_task = pickle_dump_read(task)
        assert pick_task.func.__name__ == "func_on_main_level"
        assert isfunction(pick_task.func)
        assert pick_task.end_cond is None

    def test_unpicklable_session(self, session):
        def func_nested():
            pass
        unpkl_task = FuncTask(func_nested, execution="thread", name="unpicklable", session=session)
        task = FuncTask(func_on_main_level, execution="process", name="picklable", session=session)

        assert session.tasks == {unpkl_task, task}

        pick_task = pickle_dump_read(task)
        assert pick_task.func.__name__ == "func_on_main_level"
        assert isfunction(pick_task.func)
        assert pick_task.session is not session
        pickle_dump_read(pick_task.session)

    def test_unpicklable_session_params(self, session):
        session.parameters["unpicklable"] = FuncTask(lambda:None, execution="main", name="unpicklable", session=session)
        session.parameters["picklable"] = "myval"
        task = FuncTask(func_on_main_level, execution="process", name="picklable", session=session)
        pick_task = pickle_dump_read(task)

        for attr, val in vars(pick_task.session).items():
            if attr not in ('hooks', 'returns', 'config'):
                assert val in (None, set(), {}, Parameters())
