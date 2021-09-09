
# TODO
#import pytest
import multiprocessing, itertools
from pathlib import Path
#
from redengine import Session
from redengine.tasks import PyScript
from redengine.core import Task
from redengine.tasks.loaders import YAMLTaskLoader
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


            argvalues.append(tuple(scenario[name] for name in argnames))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")

def test_find_multiple_times(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        # Create the test files
        root = Path(str(tmpdir)) / "project"
  

        finder = YAMLTaskLoader(path="project", execution="main")
        

        create_file(root / "task1.yaml", """
        class: PyScript
        name: mytask-1
        path: 'something.py'
        """)
        finder.execute_action()
        assert list(session.tasks.keys()) == ["YAMLTaskLoader", "mytask-1"]

        create_file(root / "task2.yaml", """
        class: PyScript
        name: mytask-2
        path: 'something.py'
        """)
        finder.execute_action()
        assert list(session.tasks.keys()) == ["YAMLTaskLoader", "mytask-1", "mytask-2"]

        delete_file(root / "task1.yaml")
        finder.execute_action()
        assert list(session.tasks.keys()) == ["YAMLTaskLoader", "mytask-2"]

class TestParseTasks:
    argnames = ["file", "get_expected"]
    scenarios = [
        {
            "id": "Simple script task",
            "file": {
                "path": "project/mytask-1.yaml",
                "content": """
                    name: mytask
                    start_cond: 'time of day between 10:00 and 14:00'
                    path: mytask.py
                    func: main
                """,
            },
            "get_expected": lambda: (
                PyScript(name="mytask", path="project/mytask.py", func="main", start_cond="time of day between 10:00 and 14:00", session=Session())
            )
        },
        {
            "id": "Multiple script task",
            "file": {
                "path": "project/mytask-1.yaml",
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
    ]

    def test_parse_tasks(self, tmpdir, file, get_expected, session):
        with tmpdir.as_cwd() as old_dir:
            # Create the test files
            root = Path(str(tmpdir))

            path = root / file["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file["content"])       

            finder = YAMLTaskLoader(path="project", execution="main")
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
                "project/task-1.yaml": """
                    name: get_stuff
                    start_cond: 'time of day between 10:00 and 14:00'
                    path: scripts/get_some_stuff.py
                    func: main
                """,
                "project/scripts/get_some_stuff.py": """
                    def main():
                        pass
                """,

                "project/task-2.yaml": """
                    name: do_stuff
                    start_cond: 'time of day between 22:00 and 23:00 & true'
                    path: scripts/do_some_stuff.py
                    func: do_this
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
        {
            "id": "One file",
            "files": {
                "project/task-1.yaml": """
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

            finder = YAMLTaskLoader(path="project", execution="main")
            finder.execute_action()
            parsed_tasks = [task for task in session.tasks.values() if task is not finder]

            expected_tasks = get_expected()

            for actual_task, expected_task in itertools.zip_longest(parsed_tasks, expected_tasks):
                # We don't compare sessions so let's just put them the same
                actual_task.session = session
                expected_task.session = session
                asset_task_equal(actual_task, expected_task)