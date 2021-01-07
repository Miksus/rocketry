
# TODO
#import pytest
#
#from pypipe import Scheduler, ScriptTask
#from pypipe.core.task.base import Task
#
#
#Task.use_instance_naming = True
from pypipe import session

def test_success(tmpdir, successing_script_path):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = ScriptTask(
            successing_script_path, 
            execution="daily",
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir, failing_script_path):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = ScriptTask(
            failing_script_path, 
            execution="daily",
        )
        with pytest.raises(ZeroDivisionError):
            task()
        assert task.status == "fail"