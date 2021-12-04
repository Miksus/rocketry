
import sys
from textwrap import dedent

import pytest

from redengine.parse import parse_condition
from redengine import Session

@pytest.fixture(autouse=True)
def set_sys_path(tmpdir):
    # Code that will run before your test, for example:
    sys.path.append(str(tmpdir))
    print(sys.path)
    # A test function will be run at this point
    yield
    # Code that will run after your test, for example:
    sys.path.remove(str(tmpdir))

def test_no_config():
    sess = Session.from_dict(
        {}
    )
    assert isinstance(sess, Session)

def test_full_featured(tmpdir, session):
    
    with tmpdir.as_cwd() as old_dir:

        # A throw-away file to link all pre-set tasks
        tmpdir.join("funcs.py").write(dedent("""
        def do_a_task():
            pass
        """))

        project_dir = tmpdir.mkdir("projects")

        task_1 = project_dir.mkdir("annuals")
        task_1.join("main.py").write(dedent("""
        def main():
            pass
        """))
        task_1.join("config.yaml").write(dedent("""
        start_cond: daily starting 10:00
        """))

        # Task 2 will miss config file and should never run (automatically)
        project_dir.mkdir("quarterly").join("main.py").write(dedent("""
        def main():
            pass
        """))

        sess = Session.from_dict(
            {
                "parameters": {
                    "mode": "test"
                },
                "tasks": {
                    "maintain.notify-1": {"class": "FuncTask", "func": "funcs.do_a_task", "execution": "main"},
                    "maintain.notify-start-up": {"class": "FuncTask", "func": "funcs.do_a_task", "execution": "main", "on_startup": True},
                    "maintain.notify-shut-down": {"class": "FuncTask", "func": "funcs.do_a_task", "execution": "main", "on_shutdown": True},

                    "fetch.stock-prices": {"class": "FuncTask", "func": "funcs.do_a_task"},
                    "fetch.fundamentals": {"class": "FuncTask", "func": "funcs.do_a_task", "start_cond": "daily"},
                    "calculate.signals": {"class": "FuncTask", "func": "funcs.do_a_task"},
                    "report.signals": {"class": "FuncTask", "func": "funcs.do_a_task"},

                    "maintain.pull": {"class": "FuncTask", "func": "funcs.do_a_task", "execution": "main"},
                    "maintain.status": {"class": "FuncTask", "func": "funcs.do_a_task", "execution": "main", "start_cond": "daily starting 19:00"},
                },
                "sequences": {
                    "sequence.signals-1": {
                        "interval": "time of day after 19:00", # Start condition for the first task of the sequence
                        "tasks": [
                            "fetch.stock-prices",
                            "calculate.signals",
                            "report.signals",
                        ],
                    },
                    "sequence.signals-2": {
                        "interval": "time of day before 19:00", # Start condition for the first task of the sequence
                        "tasks": [
                            "fetch.fundamentals",
                            "calculate.signals",
                            "report.signals",
                        ]
                    },
                },
                "scheduler": {
                    "name": "my_scheduler",
                    "restarting": "relaunch",
                }
            }
        )
        
        assert isinstance(sess, Session)

        # Assert found tasks
        for name, task in sess.tasks.items():
            assert name == task.name
        tasks = {task_name for task_name in sess.tasks}
        assert {
            "fetch.stock-prices", 
            "fetch.fundamentals", 
            "calculate.signals",
            "report.signals",

            # From ProjectFinder
            # "annuals",
            # "quarterly",

            "maintain.notify-1", 
            "maintain.pull",
            "maintain.status",

            "maintain.notify-start-up",
            "maintain.notify-shut-down"
        } == tasks

        assert {
            # Globals
            "mode": "test",
        } == dict(**sess.parameters)

        # Test sequences
        cond = parse_condition("daily starting 19:00")
        cond.kwargs["task"] = sess.get_task("maintain.status")
        assert sess.get_task("maintain.status").start_cond == cond



def test_scheduler_tasks_set(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        tmpdir.join("some_funcs.py").write(dedent("""
        def do_task_1():
            pass
        def do_task_2():
            pass
        def do_maintain():
            pass
        """))

        sess = Session.from_dict(
            {
                "tasks": {
                    "task_1": {"class": "FuncTask", "func": "some_funcs:do_task_1"},
                    "task_2": {"class": "FuncTask", "func": "some_funcs:do_task_2"},
                    "maintain.task_1": {"class": "FuncTask", "func": "some_funcs:do_maintain", "execution": "main"}
                },
                "scheduler": {
                    "name": "my_scheduler",
                    "restarting": "relaunch",
                    "parameters": {"param_a": 1, "param_b": 2}
                }
            }
        )
        assert isinstance(sess, Session)
        assert ["task_1", "task_2", "maintain.task_1"] == [task for task in sess.tasks]
        assert ["do_task_1", "do_task_2", "do_maintain"] == [task.func.__name__ for task in sess.tasks.values()]

        assert {"param_a": 1, "param_b": 2} == dict(**sess.parameters)
    