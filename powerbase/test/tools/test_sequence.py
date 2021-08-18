from powerbase.tools import Sequence
from powerbase.task import FuncTask

from log_helpers import log_task_record # From /test/helpers/log_helpers

def test_sequence(session, mock_datetime_now):

    task1 = FuncTask(lambda: None, name="task1", start_cond="time of day between 11:00 and 16:00")
    task2 = FuncTask(lambda: None, name="task2")
    # task3 = FuncTask(lambda: None, name="task3")

    seq = Sequence(tasks=[task1, task2], interval="time of day between 10:00 and 16:00")

    mock_datetime_now("2021-06-01 09:00:00")
    assert not bool(task1)
    assert not bool(task2)

    # Task1 start_cond has not yet started
    mock_datetime_now("2021-06-01 10:30:00")
    assert not bool(task1)
    assert not bool(task2)

    # Start of the sequence
    mock_datetime_now("2021-06-01 11:30:00")
    assert bool(task1)
    assert not bool(task2)

    # Task1 is running
    log_task_record(task=task1, action="run", now="2021-06-01 11:30:00")
    assert not bool(task1)
    assert not bool(task2)

    # Task1 ran, now task2 can run
    mock_datetime_now("2021-06-01 11:35:00")
    log_task_record(task=task1, action="success", now="2021-06-01 11:35:00")
    assert not bool(task1)
    assert bool(task2)

    # Task1 ran, task2 is running
    mock_datetime_now("2021-06-01 11:40:00")
    log_task_record(task=task2, action="run", now="2021-06-01 11:40:00")
    assert not bool(task1)
    assert not bool(task2)

    # Task1 and Task2 ran
    mock_datetime_now("2021-06-01 11:40:00")
    log_task_record(task=task1, action="fail", now="2021-06-01 11:45:00")
    assert not bool(task1)
    assert not bool(task2)

    # Now we are in the next cycle
    mock_datetime_now("2021-06-02 11:30:00")
    assert bool(task1)
    assert not bool(task2)