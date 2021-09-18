
# TODO
#import pytest
import multiprocessing, itertools
from pathlib import Path
#
from redengine import Session
from redengine.tasks import FuncTask
from redengine.core import Task
from redengine.tasks.loaders import YAMLLoader
from redengine.time import TimeOfDay
#from redengine.core.task.base import Task
#
import pandas as pd
import pytest
from textwrap import dedent

from io_helpers import create_file, delete_file


def test_loader(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        # Create some dummy tasks
        root = Path(str(tmpdir)) / "project"
        task1 = FuncTask(lambda: None, name="task-A")
        task2 = FuncTask(lambda: None, name="task-B")
        finder = YAMLLoader(path="project")
        
        create_file(root / "conftask.yaml", dedent("""
        tasks:
          task-1:
            class: PyScript
            path: 'something.py'
          task-2:
            class: PyScript
            path: 'something.py'
        sequences:
          my-sequence-1:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
        """))
        finder.execute()

        seq = session.extensions["sequences"]["my-sequence-1"]
        assert ["task-1", "task-2"] == [t.name for t in seq.tasks]
        assert TimeOfDay("12:00", "16:00") == seq.interval

        assert {"task-A", "task-B", "YAMLLoader", "task-1", "task-2"} == {t.name for t in session.tasks.values()}

        # Test the path is correct in the tasks
        assert root / "something.py" == seq.tasks[0].path