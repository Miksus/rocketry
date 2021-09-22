
# TODO
#import pytest
import multiprocessing, itertools
import os
from pathlib import Path
#
from redengine import Session
from redengine.tasks import PyScript
from redengine.core import Task
from redengine.tasks.loaders import TaskLoader
#from redengine.core.task.base import Task
#
import pandas as pd
import pytest
from textwrap import dedent
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

def test_find_multiple_times(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        # Create the test files
        root = Path(str(tmpdir)) / "project"
  
        finder = TaskLoader(path="project", execution="main")
        
        create_file(root/ "tasks.yaml", """
        mytask-1:
            class: PyScript
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-1"]

        delete_file(root / "tasks.yaml")
        create_file(root / "tasks.yaml", """
        mytask-1:
            class: PyScript
            path: 'something.py'
        mytask-2:
            class: PyScript
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-1", "mytask-2"]

        delete_file(root / "tasks.yaml")
        create_file(root / "tasks.yaml", """
        mytask-2:
            class: PyScript
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-2"]

class TestParseTasks:
    argnames = ["file", "get_expected", "kwargs"]
    scenarios = [
        {
            "id": "Simple script task",
            "file": {
                "path": "project/tasks.yaml",
                "content": """
                    - name: mytask
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: mytask.py
                      func: main
                """,
            },
            "get_expected": lambda: [
                PyScript(name="mytask", path="project/mytask.py", func="main", start_cond="time of day between 10:00 and 14:00", session=Session())
            ]
        },
        {
            "id": "Multiple script task (list)",
            "file": {
                "path": "project/tasks.yaml",
                "content": """
                    - name: mytask1
                      start_cond: 'time of day between 06:00 and 08:00'
                      path: mytask.py
                      func: main
                    - name: mytask2
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: mytask.py
                      func: myfunc
                """,
            },
            "get_expected": (lambda: [
                PyScript(name="mytask1", path="project/mytask.py", func="main", start_cond="time of day between 06:00 and 08:00", session=Session()), 
                PyScript(name="mytask2", path="project/mytask.py", func="myfunc", start_cond="time of day between 10:00 and 14:00", session=Session())
            ])
        },
        {
            "id": "Multiple script task (dict)",
            "file": {
                "path": "project/tasks.yaml",
                "content": """
                    mytask1:
                      start_cond: 'time of day between 06:00 and 08:00'
                      path: mytask.py
                      func: main
                    mytask2:
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: mytask.py
                      func: myfunc
                """,
            },
            "get_expected": (lambda: [
                PyScript(name="mytask1", path="project/mytask.py", func="main", start_cond="time of day between 06:00 and 08:00", session=Session()), 
                PyScript(name="mytask2", path="project/mytask.py", func="myfunc", start_cond="time of day between 10:00 and 14:00", session=Session())
            ])
        },
        {
            "id": "Pattern (exclude dev)",
            "file": {
                "path": "project/tasks.yaml",
                "content": """
                    dev.mytask1:
                      start_cond: 'time of day between 06:00 and 08:00'
                      path: mytask.py
                      func: main
                    mytask2:
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: mytask.py
                      func: myfunc
                """,
            },
            "get_expected": (lambda: [
                #PyScript(name="dev.mytask1", path="project/mytask.py", func="main", start_cond="time of day between 06:00 and 08:00", session=Session()), 
                PyScript(name="mytask2", path="project/mytask.py", func="myfunc", start_cond="time of day between 10:00 and 14:00", session=Session())
            ]),
            "kwargs": {"name_pattern": r"^(?!dev[.]).+"}
        },
        {
            "id": "Pattern (include dev)",
            "file": {
                "path": "project/tasks.yaml",
                "content": """
                    dev.mytask1:
                      start_cond: 'time of day between 06:00 and 08:00'
                      path: mytask.py
                      func: main
                    mytask2:
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: mytask.py
                      func: myfunc
                """,
            },
            "get_expected": (lambda: [
                PyScript(name="dev.mytask1", path="project/mytask.py", func="main", start_cond="time of day between 06:00 and 08:00", session=Session()), 
                #PyScript(name="mytask2", path="project/mytask.py", func="myfunc", start_cond="time of day between 10:00 and 14:00", session=Session())
            ]),
            "kwargs": {"name_pattern": r"dev[.].+"}
        },
    ]

    def test_parse_tasks(self, tmpdir, file, get_expected, kwargs, session):
        with tmpdir.as_cwd() as old_dir:
            # Create the test files
            root = Path(str(tmpdir))

            path = root / file["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file["content"])       

            kwargs = {} if kwargs is None else kwargs
            finder = TaskLoader(path="project", execution="main", **kwargs)
            parsed_task = finder.parse_file(file["path"])

            expected_task = get_expected()

            if isinstance(expected_task, list):
                for actual_task, expected_task in itertools.zip_longest(parsed_task, expected_task):
                    # session is of course different, forcing the same
                    expected_task.session = session
                    asset_task_equal(actual_task, expected_task)
            else:
                # session is of course different, forcing the same
                expected_task.session = session
                asset_task_equal(parsed_task, expected_task)



class TestFindTasks:
    argnames = ["files", "get_expected"]
    scenarios = [
        {
            "id": "Typical case",
            "files": {
                "project/fetch/tasks.yaml": """
                    - name: get_stuff
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: ../scripts/get_some_stuff.py
                      func: main
                """,
                "project/scripts/get_some_stuff.py": """
                    def main():
                        pass
                """,

                "project/transform/tasks.yaml": """
                    - name: do_stuff
                      start_cond: 'time of day between 22:00 and 23:00 & true'
                      path: scripts/do_some_stuff.py
                      func: do_this
                """,
                "project/transform/scripts/do_some_stuff.py": """
                    def do_this():
                        pass
                """,
            },
            "get_expected": (lambda: [
                PyScript(path="project/fetch/../scripts/get_some_stuff.py", func="main", start_cond="time of day between 10:00 and 11:00", name="get_stuff", session=Session()),
                PyScript(path="project/transform/scripts/do_some_stuff.py", func="do_this", start_cond="time of day between 22:00 and 23:00 & true", name="do_stuff", session=Session()),
            ])
        },
        {
            "id": "One file",
            "files": {
                "project/tasks.yaml": """
                    - name: get_stuff
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: scripts/get_some_stuff.py
                      func: main
                    - name: do_stuff
                      start_cond: 'time of day between 22:00 and 23:00 & true'
                      path: scripts/do_some_stuff.py
                      func: do_this
                """,

                "project/scripts/get_some_stuff.py": """
                    def main():
                        pass
                """,
                "project/scripts/do_some_stuff.py": """
                    def do_this():
                        pass
                """,
            },
            "get_expected": (lambda: [
                PyScript(path="project/scripts/get_some_stuff.py", func="main", start_cond="time of day between 10:00 and 11:00", name="get_stuff", session=Session()),
                PyScript(path="project/scripts/do_some_stuff.py", func="do_this", start_cond="time of day between 22:00 and 23:00 & true", name="do_stuff", session=Session()),
            ])
        },
    ]

    def test_find_tasks(self, tmpdir, files, get_expected, session):
        with tmpdir.as_cwd() as old_dir:
            # Create the test files
            root = Path(str(tmpdir))
            for path, cont in files.items():
                path = root / path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(cont)       

            finder = TaskLoader(path="project", execution="main")
            finder.execute()
            parsed_tasks = [task for task in session.tasks.values() if task is not finder]

            expected_tasks = get_expected()

            for actual_task, expected_task in itertools.zip_longest(parsed_tasks, expected_tasks):
                # We don't compare sessions so let's just put them the same
                actual_task.session = session
                expected_task.session = session
                asset_task_equal(actual_task, expected_task)
                if hasattr(actual_task, "path"):
                    assert os.path.isfile(actual_task.path)