import pytest

from textwrap import dedent

from pypipe.core import Scheduler
#from pypipe.builtin.task import ScriptTask
from pypipe.core.task.base import Task
from pypipe.core import reset

def test_from_project_folder(tmpdir):
    # Going to tempdir to dump the log files there
    reset()

    script_a = dedent("""
        from pypipe.core.conditions import ram_free

        START_CONDITION = ram_free(absolute=False)

        def main():
            pass
    """)

    script_b = dedent("""
        from pypipe.core.conditions import ram_free

        START_CONDITION = ram_free(absolute=True)

        def main():
            pass
    """)
    with tmpdir.as_cwd() as old_dir:
        task_folder = tmpdir.mkdir("tasks")
        task_folder.mkdir("task_a").join("main.py").write(script_a)
        task_folder.mkdir("task_b").join("main.py").write(script_b)

        tasks = ScriptTask.from_project_folder("tasks")
        assert tasks[0].name == "task_a"
        assert tasks[1].name == "task_b"

        assert tasks[0].start_cond.kwargs["absolute"] ==  False
        assert tasks[1].start_cond.kwargs["absolute"] ==  True

def test_from_module_folder(tmpdir):
    reset()

    script_a = dedent("""
        from pypipe.core.conditions import ram_free

        START_CONDITION = ram_free(absolute=False)

        def main():
            pass
    """)
    script_b = dedent("""
        from pypipe.core.conditions import ram_free

        START_CONDITION = ram_free(absolute=True)

        def main():
            pass
    """)
    with tmpdir.as_cwd() as old_dir:
        task_folder = tmpdir.mkdir("tasks")
        task_folder.join("task_a.py").write(script_a)
        task_folder.join("task_b.py").write(script_b)
        task_folder.mkdir("not_from_here").join("task_c.py").write("This should not be read")

        tasks = ScriptTask.from_module_folder("tasks")
        
        assert tasks[0].name == "task_a"
        assert tasks[1].name == "task_b"
        assert 2 == len(tasks)

        assert tasks[0].start_cond.kwargs["absolute"] ==  False
        assert tasks[1].start_cond.kwargs["absolute"] ==  True

def test_init(tmpdir, successing_script_path):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = ScriptTask(
            successing_script_path, 
            execution="daily",
        )
        assert task.status is None