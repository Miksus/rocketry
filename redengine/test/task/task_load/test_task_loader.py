
import itertools
import os
from pathlib import Path
from textwrap import dedent

import pytest

from redengine.tasks.func import FuncTask
from redengine import Session
from redengine.tasks import FuncTask
from redengine.core import Task
from redengine.tasks.loaders import TaskLoader

from io_helpers import create_file, delete_file

def asset_task_equal(a:Task, b:Task, ignore=None):
    ignore = [] if ignore is None else ignore
    assert isinstance(a, Task)
    assert isinstance(b, Task)

    assert type(a) is type(b)

    cls = type(a)
    base_clss = cls.__bases__
    attrs = list(cls.__annotations__) 
    for base_cls in base_clss:
        attrs += list(base_cls.__annotations__) 

    for attr in attrs:
        if attr in ignore:
            continue
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
    pytest.importorskip("yaml")
    with tmpdir.as_cwd() as old_dir:
        # Create the test files
        root = Path(str(tmpdir)) / "project"
  
        finder = TaskLoader(path="project", execution="main")
        
        create_file(root/ "tasks.yaml", """
        mytask-1:
            class: FuncTask
            func: 'main'
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-1"]

        delete_file(root / "tasks.yaml")
        create_file(root / "tasks.yaml", """
        mytask-1:
            class: FuncTask
            func: 'main'
            path: 'something.py'
        mytask-2:
            class: FuncTask
            func: 'main'
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-1", "mytask-2"]

        delete_file(root / "tasks.yaml")
        create_file(root / "tasks.yaml", """
        mytask-2:
            class: FuncTask
            func: 'main'
            path: 'something.py'
        """)
        finder.execute()
        assert list(session.tasks.keys()) == ["TaskLoader", "mytask-2"]


class TestParseTasks:
    argnames = ["files", "get_expected"]
    scenarios = [
        {
            "id": "FuncTasks in same folder (list)",
            "files": {
                "project/myfolder/tasks.yaml": """
                    - name: task-1
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: some_stuff.py
                      func: get_stuff
                    - name: task-2
                      start_cond: 'time of day between 22:00 and 23:00 & true'
                      path: some_stuff.py
                      func: do_stuff
                """,

                "project/myfolder/some_stuff.py": dedent("""
                    def get_stuff():
                        pass
                    def do_stuff():
                        pass
                    """),
            },
            "get_expected": (lambda: [
                FuncTask(path="project/myfolder/some_stuff.py", func="get_stuff", start_cond="time of day between 10:00 and 11:00", name="task-1", session=Session()),
                FuncTask(path="project/myfolder/some_stuff.py", func="do_stuff", start_cond="time of day between 22:00 and 23:00 & true", name="task-2", session=Session()),
            ])
        },
        {
            "id": "FuncTasks in same folder (dict)",
            "files": {
                "project/myfolder/tasks.yaml": """
                    task-1:
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: some_stuff.py
                      func: get_stuff
                    task-2:
                      start_cond: 'time of day between 22:00 and 23:00 & true'
                      path: some_stuff.py
                      func: do_stuff
                """,

                "project/myfolder/some_stuff.py": dedent("""
                    def get_stuff():
                        pass
                    def do_stuff():
                        pass
                    """),
            },
            "get_expected": (lambda: [
                FuncTask(path="project/myfolder/some_stuff.py", func="get_stuff", start_cond="time of day between 10:00 and 11:00", name="task-1", session=Session()),
                FuncTask(path="project/myfolder/some_stuff.py", func="do_stuff", start_cond="time of day between 22:00 and 23:00 & true", name="task-2", session=Session()),
            ])
        },
        {
            "id": "FuncTasks in relative folder",
            "files": {
                "project/fetch/tasks.yaml": dedent("""
                    - name: get_stuff
                      start_cond: 'time of day between 10:00 and 14:00'
                      path: ../scripts/get_some_stuff.py
                      func: main
                    """),
                "project/scripts/get_some_stuff.py": dedent("""
                    def main():
                        pass
                    """),
            },
            "get_expected": (lambda: [
                FuncTask(path="project/fetch/../scripts/get_some_stuff.py", func="main", start_cond="time of day between 10:00 and 11:00", name="get_stuff", session=Session()),
            ])
        },
    ]

    def test_find_tasks(self, tmpdir, files, get_expected, session):
        pytest.importorskip("yaml")
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