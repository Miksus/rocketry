
# TODO
#import pytest
import multiprocessing, itertools
from pathlib import Path
from redengine.tasks.loaders.yaml import YAMLTaskLoader
#
from redengine import Session
from redengine.tasks import FuncTask
from redengine.core import Task, Scheduler
from redengine.tasks.loaders import YAMLExtensionLoader, YAMLLoader
from redengine.time import TimeOfDay
from redengine.conditions import AlwaysTrue
#from redengine.core.task.base import Task
#
import pandas as pd
import pytest
from textwrap import dedent

from io_helpers import create_file, delete_file

def test_session(session, tmpdir):
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
          path: 'something.py'
        - name: 'task-2'
          path: 'something.py'
        """))
        ext_loader = YAMLExtensionLoader(on_startup=True)
        task_loader = YAMLTaskLoader(on_startup=True)

        Scheduler(shut_cond=AlwaysTrue())
        session.start()
        assert ['run', 'success'] == [rec['action'] for rec in task_loader.logger.get_records()]
        assert ['run', 'success'] == [rec['action'] for rec in ext_loader.logger.get_records()]
        assert ['YAMLExtensionLoader', 'YAMLTaskLoader', "task-1", "task-2"] == list(session.tasks.keys())
        assert ["my-sequence-1"] == list(session.extensions["sequences"].keys())