
# TODO
#import pytest
import multiprocessing
#
from powerbase.task import PyScript
from powerbase.task.meta import YAMLFinder
#from powerbase.core.task.base import Task
#
import pandas as pd
import pytest
from textwrap import dedent


@pytest.mark.parametrize("cont,expected_task", [
    pytest.param("""
        name: mytask
        start_cond: 'daily starting 08:00'
        path: mytask.py
        func: main
        """, 
        PyScript(name="mytask", path="task_dir/mytask.py", func="main", start_cond="daily starting 08:00"),
        id="Simple script task"
    ), 
    pytest.param("""
        - name: mytask1
          start_cond: 'daily starting 08:00'
          path: mytask.py
          func: main
        - name: mytask2
          start_cond: 'daily starting 08:00'
          path: mytask.py
          func: main
        """, 
        [PyScript(name="mytask1", path="task_dir/mytask.py", func="main", start_cond="daily starting 08:00"), PyScript(name="mytask2", path="task_dir/mytask.py", func="main", start_cond="daily starting 08:00")],
        id="Multiple script task"
    ), 
])
def test_parse_task(tmpdir, cont, expected_task, session):
    with tmpdir.as_cwd() as old_dir:

        task_file = tmpdir.mkdir("task_dir").join("mytask.yaml")
        task_file.write(dedent(cont))

        finder = YAMLFinder()
        parsed_task = finder.parse_file("task_dir/mytask.yaml")

        assert expected_task == parsed_task

