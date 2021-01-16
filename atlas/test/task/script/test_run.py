
# TODO
#import pytest
#
from atlas.task import ScriptTask
#from atlas.core.task.base import Task
#
#
#Task.use_instance_naming = True
from atlas import session
import pytest



@pytest.mark.parametrize(
    "script_path,expected_outcome,exc_cls",
    [
        pytest.param(
            "scripts/succeeding_script.py", 
            "success",
            None,
            id="Success"),
        pytest.param(
            "scripts/failing_script.py", 
            "fail", 
            RuntimeError,
            id="Failure"),
    ],
)
def test_run(tmpdir, script_files, script_path, expected_outcome, exc_cls):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = ScriptTask(
            script_path, 
            name="a task"
        )

        if exc_cls:
            # Failing task
            with pytest.raises(exc_cls):
                task()
        else:
            # Succeeding task
            task()

        assert task.status == expected_outcome

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": expected_outcome},
        ] == records


# Parametrization
def test_parametrization_runtime(tmpdir, script_files):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = ScriptTask(
            "scripts/parameterized_script.py", 
            name="a task",
        )

        task(integer=1, string="X", optional_float=1.1, extra_parameter="Should not be passed")

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

def test_parametrization_local(tmpdir, script_files):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = ScriptTask(
            "scripts/parameterized_script.py", 
            name="a task",
            parameters={"integer": 1, "string": "X", "optional_float": 1.1}
        )

        task()

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records