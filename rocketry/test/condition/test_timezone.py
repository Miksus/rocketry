import datetime
from time import time

import pytest
from rocketry.conditions.task.task import TaskStarted
from rocketry.conds import (
    true, false,
    every,
    daily, weekly, monthly,
    time_of_day, time_of_week, time_of_month,
    after_finish, after_success, after_fail,

    after_all_success, after_any_success, after_all_fail, after_any_fail, after_all_finish, after_any_finish,

    scheduler_running, scheduler_cycles,

    succeeded, failed, finished, started,
    running,

    cron,
    retry,
    crontime,
)
from rocketry.tasks import FuncTask

def do_success(): ...
def do_failure(): raise RuntimeError("Oops")

class Timer:

    def __init__(self, start:datetime.datetime):
        self.start = start
        self.anchor = time()

    def get_time(self):
        offset = datetime.timedelta(seconds=time() - self.anchor)
        return (self.start + offset).timestamp()

def test_time_of(session):
    utc_time = datetime.timezone(datetime.timedelta(hours=0))
    timezone = datetime.timezone(datetime.timedelta(hours=12))
    # year 2024 starts on Monday
    time = Timer(datetime.datetime(2024, 1, 1, 22, 00, tzinfo=utc_time))

    session.config.time_func = time.get_time

    session.config.timezone = timezone

    # Time is 08:00 in UTC but 22:00 in GMT+10
    assert time_of_day.between("10:00", "10:05").observe(session=session)
    assert crontime("0-5 10 * * *").observe(session=session)
    assert time_of_week.on("Tuesday").observe(session=session)
    assert time_of_month.on("2nd").observe(session=session)

def test_task(session):
    utc_time = datetime.timezone(datetime.timedelta(hours=0))
    timezone = datetime.timezone(datetime.timedelta(hours=12))
    # year 2024 starts on Monday
    time = Timer(datetime.datetime(2024, 1, 1, 22, 00, tzinfo=utc_time))

    session.config.time_func = time.get_time
    session.config.timezone = timezone

    task = FuncTask(lambda: None, execution="async", session=session)

    assert daily.between("10:00", "10:05").observe(task=task, session=session)
    assert weekly.on("Tuesday").observe(task=task, session=session)
    assert monthly.on("2nd").observe(task=task, session=session)

    task.log_running()
    task.log_success()
    task.log_failure()
    task.log_termination()
    task.log_inaction()

    assert not daily.between("10:00", "10:05").observe(task=task, session=session)
    assert not weekly.on("Tuesday").observe(task=task, session=session)
    assert not monthly.on("2nd").observe(task=task, session=session)

def test_task_attrs(session):
    utc_time = datetime.timezone(datetime.timedelta(hours=0))
    timezone = datetime.timezone(datetime.timedelta(hours=12))
    # year 2024 starts on Monday
    time = Timer(datetime.datetime(2024, 1, 1, 22, 00, tzinfo=utc_time))

    session.config.time_func = time.get_time
    session.config.timezone = timezone

    task = FuncTask(lambda: None, execution="async", session=session)

    task.log_running()
    task.log_success()
    task.log_failure()
    task.log_termination()
    task.log_inaction()

    start = datetime.datetime(2024, 1, 1, 22, 0, tzinfo=utc_time)
    end = datetime.datetime(2024, 1, 1, 22, 1, tzinfo=utc_time)
    assert start <= task.last_run <= end
    assert start <= task.last_fail <= end
    assert start <= task.last_success <= end
    assert start <= task.last_terminate <= end
    assert start <= task.last_inaction <= end

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
def test_task_run(session, execution):
    utc_time = datetime.timezone(datetime.timedelta(hours=0))
    timezone = datetime.timezone(datetime.timedelta(hours=12))
    # year 2024 starts on Monday
    time = Timer(datetime.datetime(2024, 1, 1, 22, 00, tzinfo=utc_time))
 
    session.config.timezone = timezone

    task = FuncTask(do_success, start_cond=true, execution=execution, session=session)

    session.config.time_func = time.get_time
    session.config.shut_cond = TaskStarted(task=task)
    session.start()

    start = datetime.datetime(2024, 1, 1, 22, 0, tzinfo=utc_time)
    end = datetime.datetime(2024, 1, 1, 22, 5, tzinfo=utc_time)
    assert start <= task.last_run <= end
    assert start <= task.last_success <= end

    records = task.logger.filter_by().all()
    for rec in records:
        assert start.timestamp() <= rec.created <= end.timestamp()
