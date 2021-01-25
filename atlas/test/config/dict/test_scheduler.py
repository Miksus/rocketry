
from atlas.config import parse_dict

from atlas.core import Scheduler, MultiScheduler

from atlas.conditions import AlwaysFalse
from atlas.parse import parse_condition_clause

from textwrap import dedent
from atlas import session

import sys

def test_minimal():
    scheduler = parse_dict(
        {"scheduler": {}}
    )
    assert isinstance(scheduler, Scheduler)

def test_basic_scheduler(tmpdir):
    session.reset()
    with tmpdir.as_cwd() as old_dir:
        sys.path.append(str(tmpdir))
        tmpdir.join("funcs.py").write(dedent("""
        def do_task_1():
            pass
        def do_task_2():
            pass
        def do_maintain():
            pass
        """))

        scheduler = parse_dict(
            {
                "scheduler": {
                    "name": "my_scheduler",
                    "restarting": "relaunch",
                    "tasks": {
                        "task_1": {"class": "FuncTask", "func": "funcs.do_task_1"},
                        "task_2": {"class": "FuncTask", "func": "funcs.do_task_2"},
                    },
                    "maintainer_tasks": {
                        "maintain.task_1": {"class": "FuncTask", "func": "funcs.do_maintain"}
                    },
                    "parameters": {"param_a": 1, "param_b": 2}
                }
            }
        )
        assert isinstance(scheduler, Scheduler)
        assert ["task_1", "task_2"] == [task.name for task in scheduler.tasks]
        assert ["do_task_1", "do_task_2"] == [task.func.__name__ for task in scheduler.tasks]

        assert ["maintain.task_1"] == [task.name for task in scheduler.maintainer_tasks]
        assert ["do_maintain"] == [task.func.__name__ for task in scheduler.maintainer_tasks]

        assert {"param_a": 1, "param_b": 2} == dict(**scheduler.parameters)
        sys.path.remove(str(tmpdir))

def test_strategy_project_finder(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        sys.path.append(str(tmpdir))
        project_dir = tmpdir.mkdir("projects")

        task_1 = project_dir.mkdir("task_1")
        task_1.join("main.py").write(dedent("""
        def main():
            pass
        """))
        task_1.join("config.yaml").write(dedent("""
        start_cond: daily starting 10:00
        """))

        # Task 2 will miss config file and should never run (automatically)
        project_dir.mkdir("task_2").join("main.py").write(dedent("""
        def main():
            pass
        """))

        scheduler = parse_dict(
            {
                "scheduler": {
                    "name": "my_scheduler",
                    "restarting": "relaunch",
                },
                "strategy": {
                    "auto_refresh": False,
                    "tasks": [
                        {"class": "ProjectFinder", "path": "projects"}
                    ]
                }
            }
        )
        assert isinstance(scheduler, Scheduler)
        assert ["task_1", "task_2"] == [task.name for task in scheduler.tasks]
        assert [r"projects\task_1\main.py", r"projects\task_2\main.py"] == [str(task.path) for task in scheduler.tasks]

        cond_task_1 = parse_condition_clause("daily starting 10:00")
        cond_task_1.kwargs["task"] = scheduler.tasks[0]
        assert [cond_task_1, AlwaysFalse()] == [task.start_cond for task in scheduler.tasks]

        #assert ["maintain.task_1"] == [task.name for task in scheduler.maintainer_tasks]
        #assert ["do_maintain"] == [task.func.__name__ for task in scheduler.maintainer_tasks]
    
        sys.path.remove(str(tmpdir))