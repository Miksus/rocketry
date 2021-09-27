
import itertools
from pathlib import Path
from textwrap import dedent

from redengine import Session
from redengine.tasks import FuncTask
from redengine.core import Task
from redengine.tasks.loaders import PyLoader
from redengine.conditions import true

from io_helpers import create_file, delete_file

def asset_task_equal(a:Task, b:Task):
    assert isinstance(a, Task)
    assert isinstance(b, Task)

    assert type(a) is type(b)

    cls = type(a)
    base_clss = cls.__bases__
    attrs = list(cls.__annotations__) 
    for base_cls in base_clss:
        attrs += list(base_cls.__annotations__) 

    for attr in attrs:
        a_attr_val = getattr(a, attr)
        b_attr_val = getattr(b, attr)
        assert a_attr_val == b_attr_val


def pytest_generate_tests(metafunc):
    if metafunc.cls is not None:
        # This is for TestFindTasks
        idlist = []
        argvalues = []

        schenarios = metafunc.cls.scenarios
        argnames = metafunc.cls.argnames
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario.pop("id"))

            argvalues.append(tuple(scenario.get(name) for name in argnames))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestTasks:
    argnames = ["file", "get_expected", "kwargs"]
    scenarios = [
        {
            "id": "Simple task",
            "file": {
                "path": "project/pyloader_test1/tasks.py",
                "content": """
                from redengine.tasks import FuncTask

                @FuncTask
                def mytask():
                    ...
                """,
            },
            "get_expected": lambda: [
                FuncTask(func=lambda: "mytask", name="pyloader_test1.tasks:mytask", session=Session())
            ]
        },
        {
            "id": "Tasks with arguments",
            "file": {
                "path": "project/pyloader_test2/tasks.py",
                "content": """
                from redengine.tasks import FuncTask
                from redengine.conditions import true

                @FuncTask(name="mytask-1", start_cond="time of day between 10:00 and 14:00")
                def mytask():
                    ...

                @FuncTask(name="mytask-2", start_cond=true)
                def mytask():
                    ...
                """,
            },
            "get_expected": lambda: [
                FuncTask(func=lambda: "mytask", name="mytask-1", start_cond="time of day between 10:00 and 14:00", session=Session()),
                FuncTask(func=lambda: "mytask", name="mytask-2", start_cond=true, session=Session()),
            ]
        },
    ]

    def test_parse_tasks(self, tmpdir, file, get_expected, kwargs, session):
        with tmpdir.as_cwd() as old_dir:
            # Create the test files
            root = Path(str(tmpdir))

            path = root / file["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(dedent(file["content"]))       

            kwargs = {} if kwargs is None else kwargs
            finder = PyLoader(path="project", **kwargs)
            finder.execute()

            actual_tasks = session.tasks.values()
            expected_tasks = [finder] + get_expected()

            if isinstance(expected_tasks, list):
                for actual_task, expected_task in itertools.zip_longest(actual_tasks, expected_tasks):
                    if expected_task is finder:
                        asset_task_equal(actual_task, expected_task)
                        continue
                    # session is of course different, forcing the same
                    expected_task.session = session
                    # We use convention: expected task's func should return name of the func
                    assert actual_task.func.__name__ == expected_task.func()
                    expected_task._func = None
                    actual_task._func = None
                    asset_task_equal(actual_task, expected_task)
            else:
                # session is of course different, forcing the same
                expected_tasks.session = session
                asset_task_equal(actual_tasks, expected_tasks)
