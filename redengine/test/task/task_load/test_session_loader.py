
from pathlib import Path
from textwrap import dedent

import pytest

from redengine.tasks import FuncTask
from redengine.tasks.loaders import SessionLoader
from redengine.time import TimeOfDay

from io_helpers import create_file, delete_file


def test_session_loader(tmpdir, session):
    pytest.importorskip("yaml")
    with tmpdir.as_cwd() as old_dir:
        # Create some dummy tasks
        root = Path(str(tmpdir)) / "project"
        task1 = FuncTask(lambda: None, name="task-A", execution="main")
        task2 = FuncTask(lambda: None, name="task-B", execution="main")
        finder = SessionLoader(path="project")
        
        create_file(root / "conftask.yaml", dedent("""
        tasks:
          task-1:
            class: FuncTask
            path: 'something.py'
            func: 'main'
          task-2:
            class: FuncTask
            path: 'something.py'
            func: 'main'
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

        assert {"task-A", "task-B", "SessionLoader", "task-1", "task-2"} == {t.name for t in session.tasks.values()}

        # Test the path is correct in the tasks
        assert root / "something.py" == seq.tasks[0].path