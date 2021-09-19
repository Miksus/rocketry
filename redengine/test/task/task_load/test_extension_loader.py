
# TODO
#import pytest
import multiprocessing, itertools
from pathlib import Path
#
from redengine import Session
from redengine.tasks import FuncTask
from redengine.core import Task
from redengine.tasks.loaders import YAMLExtensionLoader
from redengine.time import TimeOfDay
#from redengine.core.task.base import Task
#
import pandas as pd
import pytest
from textwrap import dedent

from io_helpers import create_file, delete_file

def test_loader_multiple_times(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        # Create some dummy tasks
        FuncTask(lambda: None, name="task-1")
        FuncTask(lambda: None, name="task-2")
        root = Path(str(tmpdir)) / "project"

        finder = YAMLExtensionLoader(path="project")
        
        create_file(root / "extensions.yaml", dedent("""
        sequences:
          my-sequence-1:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
        """))
        finder.execute()
        assert list(session.extensions["sequences"].keys()) == ["my-sequence-1"]
        assert "Sequence(tasks=['task-1', 'task-2'], interval=TimeOfDay('12:00', '16:00'))" == repr(session.extensions["sequences"]["my-sequence-1"])

        delete_file(root / "extensions.yaml")
        create_file(root / "extensions.yaml", dedent("""
        sequences:
          my-sequence-1:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
          my-sequence-2:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
          my-sequence-3:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
        """))
        finder.execute()
        assert list(session.extensions["sequences"].keys()) == ["my-sequence-1", "my-sequence-2", "my-sequence-3"]

        delete_file(root / "extensions.yaml")
        create_file(root / "extensions.yaml", dedent("""
        sequences:
          my-sequence-2:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
          my-sequence-3:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
        """))
        finder.execute()
        assert list(session.extensions["sequences"].keys()) == ["my-sequence-2", "my-sequence-3"]
        
        delete_file(root / "extensions.yaml")
        finder.execute()
        assert [] == list(session.extensions["sequences"].keys())

def test_loader(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        # Create some dummy tasks
        task1 = FuncTask(lambda: None, name="task-1")
        task2 = FuncTask(lambda: None, name="task-2")
        root = Path(str(tmpdir)) / "project"

        finder = YAMLExtensionLoader(path="project")
        
        create_file(root / "extensions.yaml", dedent("""
        sequences:
          my-sequence-1:
            tasks:
              - task-1
              - task-2
            interval: 'time of day between 12:00 and 16:00'
        """))
        finder.execute()

        seq = session.extensions["sequences"]["my-sequence-1"]
        assert [task1, task2] == seq.tasks
        assert TimeOfDay("12:00", "16:00") == seq.interval