import asyncio
import logging
from textwrap import dedent
from pyparsing import sys
import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo, CSVFileRepo

from rocketry import Rocketry
from rocketry.conditions.task.task import TaskStarted
from rocketry.args import Return, Arg, FuncArg
from rocketry import Session
from rocketry.tasks import CommandTask
from rocketry.tasks import FuncTask
from rocketry.conds import false, true

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

@pytest.mark.parametrize("execution", ["main", "async", "thread"])
def test_command(tmpdir, execution):
    set_logging_defaults()

    py_file = tmpdir.join("myfile.py")
    py_file.write(dedent("""
        from pathlib import Path
        (Path(__file__).parent / "finish.txt").write_text("Success")
        print("Hello world")
        """
    ))

    app = Rocketry(config={'task_execution': 'main'})
    app.task(true, command=[sys.executable, str(py_file)], execution=execution, name="do_things")

    app.session.config.shut_cond = TaskStarted(task='do_things')
    app.run()
    logger = app.session['do_things'].logger

    assert logger.filter_by(action="success").count() == 1
    assert (tmpdir / "finish.txt").exists()
    assert app.session.returns[app.session['do_things']].startswith("Hello world")

@pytest.mark.parametrize("execution", ["main", "async", "thread"])
def test_command_params(tmpdir, execution):
    set_logging_defaults()

    py_file = tmpdir.join("myfile.py")
    py_file.write(dedent("""
        import sys
        assert sys.argv[1:] == ['--report-date', '2022-01-01', '--env', 'test']
        """
    ))

    app = Rocketry(config={'task_execution': 'main'})
    app.task(true, command=[sys.executable, str(py_file)], execution=execution, parameters={"--report-date": "2022-01-01", "env": "test"}, name="do_things")

    app.session.config.shut_cond = TaskStarted(task='do_things')
    app.run()
    logger = app.session['do_things'].logger

    assert logger.filter_by(action="success").count() == 1

@pytest.mark.parametrize("execution", ["main", "async", "thread"])
def test_command_fail(tmpdir, execution):
    set_logging_defaults()

    py_file = tmpdir.join("myfile.py")
    py_file.write(dedent("""
        raise RuntimeError("Oops")
        """
    ))

    app = Rocketry(config={'task_execution': 'main'})
    app.task(true, command=[sys.executable, str(py_file)], execution=execution, name="do_things")

    app.session.config.shut_cond = TaskStarted(task='do_things')
    app.run()
    logger = app.session['do_things'].logger
    
    assert logger.filter_by(action="fail").count() == 1
    assert 'raise RuntimeError("Oops")' in logger.filter_by(action="fail").all()[0].exc_text

def test_command_process(tmpdir):
    set_logging_defaults()

    app = Rocketry(config={'task_execution': 'main'})
    with pytest.raises(UserWarning):
        app.task(true, command=[sys.executable, "-V"], execution="process", name="do_things")
