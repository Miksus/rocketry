
from pathlib import Path
import importlib
import importlib.util
import sys, os

import pytest

from redengine.conditions.scheduler import SchedulerCycles
from redengine.cli import main

def test_create_default(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("myproject").is_dir()

        main(["create", "myproject"])
        assert Path("myproject").is_dir()
        assert Path("myproject/tasks").is_dir()
        assert Path("myproject/main.py").is_file()

class CLIBase:

    template = None

    @pytest.fixture#(scope="class")
    def project(self, tmpdir):
        with tmpdir.as_cwd() as old_dir:
            main(["create", "myproject", "--template", self.template])
            project_root = os.path.join(str(tmpdir), "myproject")
            sys.path.append(project_root)
            yield project_root
            sys.path.remove(project_root)


    def test_start(self, project):
        module = importlib.import_module("main")

        session = module.session
        session.set_as_default()
        
        # Make almost instant shutdown
        session.scheduler.shut_cond = SchedulerCycles() == 1
        session.start()

        assert 1 < len(session.tasks)

        # Check no tasks failed
        assert ["success"] * len(session.tasks) == [
            task.status
            for task in session.tasks.values()
        ]

class TestStandalone(CLIBase):
    template = "standalone"

    def test_content(self, project):
        assert os.listdir(project) == ["main.py"]

class TestMinimal(CLIBase):
    template = "minimal"

class TestSimple(CLIBase):
    template = "simple"
