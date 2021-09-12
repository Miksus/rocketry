
import time
import multiprocessing
from pathlib import Path
import platform

from redengine.tasks import CommandTask

import pandas as pd
import pytest
from textwrap import dedent

from task_helpers import wait_till_task_finish

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_success_command(tmpdir, session, execution):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("test.txt").is_file()

        task = CommandTask(
            command=["python", "-c", "open('test.txt', 'w');"], 
            name="a task",
            shell=False,
            execution="main"
        )
        assert task.status is None

        task()
        wait_till_task_finish(task)

        assert Path("test.txt").is_file()
        assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_fail_command(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:

        task = CommandTask(
            command=["python", "--not_an_arg"], 
            name="a task",
            shell=False,
            execution=execution
        )
        assert task.status is None

        if execution == "main":
            with pytest.raises(OSError):
                task()
        else:
            task()

        wait_till_task_finish(task)

        logs = list(task.get_history())
        assert "fail" == task.status
        assert logs[1]["exc_text"].strip().replace('\r', '').endswith(dedent("""
        OSError: Failed running command (2): 
        unknown option --not_an_arg
        usage: python [option] ... [-c cmd | -m mod | file | -] [arg] ...
        Try `python -h' for more information.""")[1:])

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_success_bat_file(tmpdir, execution, session):
    if platform.system() != "Windows":
        pytest.skip("Bat files only runnable on Windows.")

    with tmpdir.as_cwd() as old_dir:
        assert not Path("test.txt").is_file()

        file = tmpdir.join("my_command.bat")
        file.write('python -c "{code}"'.format(code="open('test.txt', 'w');"))

        task = CommandTask(
            command=["my_command.bat"], 
            name="a task",
            shell=False,
            execution="main"
        )
        assert task.status is None

        task()
        wait_till_task_finish(task)

        assert Path("test.txt").is_file()
        assert "success" == task.status


def test_success_bash_file(tmpdir, session):
    if platform.system() == "Windows":
        pytest.skip("Bash files not runnable on Windows.")
        
    with tmpdir.as_cwd() as old_dir:
        assert not Path("test.txt").is_file()

        file = tmpdir.join("my_command.bash")
        file.write('python3 -c "{code}"'.format(code="open('test.txt', 'w');"))

        task = CommandTask(
            command=["my_command.bash"], 
            name="a task",
            shell=False,
            execution="main"
        )
        assert task.status is None

        task()
        wait_till_task_finish(task)

        assert Path("test.txt").is_file()
        assert "success" == task.status