from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.conditions import AlwaysTrue, TaskStarted
from atlas import session

import pandas as pd
from typing import Generator
from itertools import chain
import datetime

import pytest

import os

def create_line_to_startup_file():
    with open("start.txt", "w") as file:
        file.write("line created\n")

def create_line_to_shutdown():
    with open("shut.txt", "w") as file:
        file.write("line created\n")


@pytest.mark.parametrize(
    "query,expected",
    [
        pytest.param(
            {"action": "run"}, 
            [
                {'task_name': 'task1', 'asctime': datetime.datetime(2021, 1, 1, 0, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task2', 'asctime': datetime.datetime(2021, 1, 1, 1, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            id="Get running"),
        pytest.param(
            {"action": ["success", "fail"]}, 
            [
                {'task_name': 'task1', 'asctime': datetime.datetime(2021, 1, 1, 4, 0, 0), 'action': 'success', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'end': datetime.datetime(2021, 1, 1, 4, 0, 0), 'runtime': '4:00:00', 'message': ''},
                {'task_name': 'task2', 'asctime': datetime.datetime(2021, 1, 1, 5, 0, 0), 'action': 'fail',    'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'end': datetime.datetime(2021, 1, 1, 5, 0, 0), 'runtime': '4:00:00', 'message': "Task 'task2' failed\nNoneType: None"},
            ],
            id="get succees & failure"),
        pytest.param(
            {"asctime": ("2021-01-01 02:00:00,000", "2021-01-01 03:00:00,000")}, 
            [
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            id="get time span (str)"),
        pytest.param(
            {"asctime": (pd.Timestamp("2021-01-01 02:00:00"), pd.Timestamp("2021-01-01 03:00:00"))}, 
            [
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            id="get time span (pd.Timestamp)"),
        pytest.param(
            {"asctime": (None, pd.Timestamp("2021-01-01 03:00:00")), "action": "run"}, 
            [
                {'task_name': 'task1', 'asctime': datetime.datetime(2021, 1, 1, 0, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task2', 'asctime': datetime.datetime(2021, 1, 1, 1, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            id="get time span (pd.Timestamp, open left)"),
        pytest.param(
            {"asctime": (pd.Timestamp("2021-01-01 02:00:00"), None), "action": "run"}, 
            [
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            id="get time span (pd.Timestamp, open right)"),
        pytest.param(
            {"asctime": (datetime.datetime(2021, 1, 1, 2, 0, 0), datetime.datetime(2021, 1, 1, 3, 0, 0))}, 
            [
                {'task_name': 'task3', 'asctime': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'end': '', 'runtime': '', 'message': ''},
                {'task_name': 'task4', 'asctime': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'end': '', 'runtime': '', 'message': ''},
            ],
            marks=pytest.mark.xfail(reason="timerange passed as datetime but datetime is mocked and isinstance fails"),
            id="get time span (datetime)"),
    ],
)
def test_get_logs_params(tmpdir, mock_pydatetime, mock_time, query, expected):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        task1 = FuncTask(lambda: None, name="task1", execution="main", force_run=True)
        task2 = FuncTask(lambda: None, name="task2", execution="main", force_run=True)
        task3 = FuncTask(lambda: None, name="task3", execution="main", force_run=True)
        task4 = FuncTask(lambda: None, name="task4", execution="main", force_run=True)

        # Start
        mock_pydatetime("2021-01-01 00:00:00")
        task1.log_running()

        mock_pydatetime("2021-01-01 01:00:00")
        task2.log_running()

        mock_pydatetime("2021-01-01 02:00:00")
        task3.log_running()

        mock_pydatetime("2021-01-01 03:00:00")
        task4.log_running()

        # Action
        mock_pydatetime("2021-01-01 04:00:00")
        task1.log_success()

        mock_pydatetime("2021-01-01 05:00:00")
        task2.log_failure()

        mock_pydatetime("2021-01-01 06:00:00")
        task3.log_inaction()  

        mock_pydatetime("2021-01-01 07:00:00")
        task4.log_termination()  
    
        #scheduler()
        
        logs = session.get_task_log(**query)
        assert isinstance(logs, chain)
        
        logs = list(logs)
        assert expected == logs