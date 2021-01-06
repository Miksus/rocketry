
# TODO
#import pytest
#
#from pypipe import Scheduler, ScriptTask
#from pypipe.core.task.base import Task
#from pypipe.core import reset
#
#Task.use_instance_naming = True


def test_success(tmpdir, successing_script_path):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = ScriptTask(
            successing_script_path, 
            execution="daily",
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir, failing_script_path):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = ScriptTask(
            failing_script_path, 
            execution="daily",
        )
        with pytest.raises(ZeroDivisionError):
            task()
        assert task.status == "fail"