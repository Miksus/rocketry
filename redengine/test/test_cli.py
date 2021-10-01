
from redengine.conditions.scheduler import SchedulerCycles
from redengine.cli import main
from pathlib import Path

import importlib
import importlib.util
import sys, os

def load_module(mdl):
    return importlib.import_module(mdl)

def test_create(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("myproject").is_dir()

        main(["create", "myproject"])
        assert Path("myproject").is_dir()
        assert Path("myproject/tasks").is_dir()
        assert Path("myproject/main.py").is_file()

def test_minimal(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("myproject").is_dir()

        main(["create", "myproject", "--template", "minimal"])
        
        try:
            sys_path = os.path.join(str(tmpdir), "myproject")
            sys.path.append(sys_path)
            module = load_module("main")

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
        finally:
            sys.path.remove(sys_path)