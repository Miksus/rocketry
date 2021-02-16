
# TODO
#import pytest
#
from atlas.task import PyScript
#from atlas.core.task.base import Task
#
#
#Task.use_instance_naming = True
from atlas import session
import pytest
from textwrap import dedent



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
        task = PyScript(
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
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": expected_outcome},
        ] == records


def test_run_specified_func(tmpdir):
    task_dir = tmpdir.mkdir("mytasks")
    task_dir.join("myfile.py").write(dedent("""
    def myfunc():
        pass
    """))

    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = PyScript(
            "mytasks/myfile.py", 
            func="myfunc",
            name="a task"
        )
        task()

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records


def test_import_relative(tmpdir):
    task_dir = tmpdir.mkdir("mytasks")
    task_dir.join("myfile.py").write(dedent("""
    from utils import value
    def main():
        assert value == 5
    """))

    task_dir.join("utils.py").write(dedent("""
    value = 5
    """))

    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = PyScript(
            "mytasks/myfile.py", 
            name="a task"
        )
        task()

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records


# Parametrization
def test_parametrization_runtime(tmpdir, script_files):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = PyScript(
            "scripts/parameterized_script.py", 
            name="a task",
        )

        task(integer=1, string="X", optional_float=1.1, extra_parameter="Should not be passed")

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

def test_parametrization_local(tmpdir, script_files):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = PyScript(
            "scripts/parameterized_script.py", 
            name="a task",
            parameters={"integer": 1, "string": "X", "optional_float": 1.1}
        )

        task()

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records