
from redengine.conditions.scheduler import SchedulerCycles
from redengine.cli import main
from pathlib import Path

import importlib
import importlib.util

def load_module(path):
    
    spec = importlib.util.spec_from_file_location("main", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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
        
        module = load_module("myproject/main.py")
        session = module.session
        
        # Make almost instant shutdown
        session.scheduler.shut_cond = SchedulerCycles() == 1
        session.start()

        assert 1 < len(session.tasks)

        # Check no tasks failed
        assert ["success"] * len(session.tasks) == [
            task.status
            for task in session.tasks.values()
        ]
