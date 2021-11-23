
from pathlib import Path

from textwrap import dedent

import pytest

from redengine.tasks.loaders import TaskLoader
from redengine.core import Scheduler
from redengine.tasks.loaders import ExtensionLoader
from redengine.conditions import AlwaysTrue

from io_helpers import create_file, delete_file

def test_session(session, tmpdir):
    pytest.importorskip("yaml")
    with tmpdir.as_cwd() as old_dir:
        root = Path(str(tmpdir)) / "project"

        create_file(root / "extensions.yaml", dedent("""
        sequences:
            my-sequence-1:
                tasks:
                    - task-1
                    - task-2
                interval: 'time of day between 12:00 and 16:00'
        """))
        create_file(root / "tasks.yaml", dedent("""
        - name: 'task-1'
          func: 'main'
          path: 'something.py'
        - name: 'task-2'
          func: 'main'
          path: 'something.py'
        """))
        ext_loader = ExtensionLoader(on_startup=True)
        task_loader = TaskLoader(on_startup=True)

        Scheduler(shut_cond=AlwaysTrue())
        session.start()
        assert ['run', 'success'] == [rec['action'] for rec in task_loader.logger.get_records()]
        assert ['run', 'success'] == [rec['action'] for rec in ext_loader.logger.get_records()]
        assert ['ExtensionLoader', 'TaskLoader', "task-1", "task-2"] == list(session.tasks.keys())
        assert ["my-sequence-1"] == list(session.extensions["sequences"].keys())