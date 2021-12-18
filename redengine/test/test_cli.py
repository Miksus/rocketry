
from pathlib import Path
import importlib
import importlib.util
import sys, os

import pytest

from redengine.conditions.scheduler import SchedulerCycles
from redengine.cli import main
from redengine import Session

def test_create_default(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("myproject").is_dir()

        main(["create", "myproject"])
        assert Path("myproject").is_dir()
        assert Path("myproject/tasks").is_dir()
        assert Path("myproject/main.py").is_file()

class CLIBase:

    template = None
    n_success = 1
    @pytest.fixture#(scope="class")
    def project(self, tmpdir):
        with tmpdir.as_cwd() as old_dir:
            main(["create", "myproject", "--template", self.template])
            project_root = os.path.join(str(tmpdir), "myproject")
            sys.path.append(project_root)
            yield project_root
            sys.path.remove(project_root)


    def test_start(self, project):
        Session(config={'task_pre_exist': 'replace'})
        module = importlib.import_module("main")
        importlib.reload(module)

        session = module.session
        session.set_as_default()
        
        # Make almost instant shutdown
        session.scheduler.shut_cond = SchedulerCycles() >= 2
        session.start()

        assert 1 < len(session.tasks)

        # Check no tasks failed
        statuses = [
            task.status
            for task in session.tasks.values()
        ]
        assert [status for status in statuses if status not in ('success', None)] == []
        assert len([status for status in statuses]) >= self.n_success
        

class TestStandalone(CLIBase):
    template = "standalone"
    n_success = 4

    def test_content(self, project):
        assert os.listdir(project) == ["main.py"]

class TestSimple(CLIBase):
    template = "simple"
    n_success = 15

    def test_start(self, project):
        pytest.importorskip('flask')
        super().test_start(project)