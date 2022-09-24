import pytest

from rocketry.conditions import (
    Retry
)

from .test_time import setup_task_state

def test_construct():
    assert Retry().n == 1
    assert Retry(2).n == 2
    assert Retry(n=2).n == 2
    assert Retry(n=0).n == 0
    assert Retry(n=-1).n == -1
    assert Retry(n=None).n == -1


@pytest.mark.parametrize(
    "cond,logs,time_after",
    [
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (failed once)"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "fail"),
                ("2020-01-01 07:05", "run"),
                ("2020-01-01 07:10", "success"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (success and failed once)"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "fail"),
                ("2020-01-01 07:05", "run"),
                ("2020-01-01 07:10", "terminate"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (terminated and failed once)"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "fail"),
                ("2020-01-01 07:05", "run"),
                ("2020-01-01 07:10", "crash"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (crashed and failed once)"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "fail"),
                ("2020-01-01 07:05", "run"),
                ("2020-01-01 07:10", "inaction"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (inacted and failed once)"),
        pytest.param(
            Retry(n=2),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "success"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry twice (failed twice)"),
        pytest.param(
            Retry(n=None),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "success"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry infinite"),
    ],
)
def test_retry(mock_datetime_now, logs, time_after, cond, session):
    session.config.force_status_from_logs = True
    task = setup_task_state(mock_datetime_now, logs, time_after, session=session)
    task.start_cond = cond
    assert cond.observe(task=task)

@pytest.mark.parametrize(
    "cond,logs,time_after",
    [
        pytest.param(
            Retry(n=1),
            [],
            "2020-01-01 07:30",
            id="No logs"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run")
            ],
            "2020-01-01 07:30",
            id="Running"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "success"),
            ],
            "2020-01-01 07:30",
            id="Succeeded"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "terminate"),
            ],
            "2020-01-01 07:30",
            id="Terminated"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "crash"),
            ],
            "2020-01-01 07:30",
            id="Crashed"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "inaction"),
            ],
            "2020-01-01 07:30",
            id="Inacted"),
        pytest.param(
            Retry(n=1),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry once (failed twice)"),
        pytest.param(
            Retry(n=2),
            [
                ("2020-01-01 07:00", "run"),
                ("2020-01-01 07:05", "fail"),
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
                ("2020-01-01 07:20", "run"),
                ("2020-01-01 07:25", "fail"),
            ],
            "2020-01-01 07:30",
            id="Retry twice (failed three times)"),
    ],
)
def test_not_retry(mock_datetime_now, logs, time_after, cond, session):
    session.config.force_status_from_logs = True
    task = setup_task_state(mock_datetime_now, logs, time_after, session=session)
    task.start_cond = cond
    assert not cond.observe(task=task)

@pytest.mark.parametrize("status", ['success', 'fail', None, 'crash', 'terminate'])
def test_retry_never(mock_datetime_now, status, session):
    session.config.force_status_from_logs = True
    logs = [('2020-01-01 07:00', 'run'), ('2020-01-01 07:10', status)] if status is not None else []

    task = setup_task_state(mock_datetime_now, logs, '2020-01-01 07:20', session=session)
    assert not Retry(0).observe(task=task)
