from powerbase.parse.condition import parse_condition_string
from _pytest.fixtures import fixture
from powerbase.components import Sequence
from powerbase.components.piping import TriggerCluster
from powerbase.conditions import All
from powerbase.task import FuncTask
from powerbase.config import parse_dict

from log_helpers import log_task_record # From /test/helpers/log_helpers

import pytest

def test_other_conditions(session, mock_datetime_now):
    "Test that the task's condition is indeed as All(other_conds, TriggerCLuster())"
    task1 = FuncTask(lambda: None, name="task1", start_cond="time of day between 11:00 and 16:00")
    task2 = FuncTask(lambda: None, name="task2")
    seq = Sequence(tasks=[task1.name, task2.name])

    mock_datetime_now("2021-06-01 09:00:00")
    assert not bool(task1)
    mock_datetime_now("2021-06-01 11:15:00")
    assert bool(task1)

class PipingBase:

    _tick = 0
    _n_tasks = 4

    def get_next_time(self):
        n = self._tick
        self._tick += 1
        return f"2021-05-31 09:{n:02d}:00"

    @pytest.fixture
    def tasks(self, request, mock_datetime_now):
        
        tasks = [
            FuncTask(lambda: None, name=f"task_{i}")
            for i in range(self._n_tasks)
        ]
        if request.param == "no previous runs":
            pass
        elif request.param == "last line success":
            for task in tasks:
                log_task_record(task=task, action="run", now=self.get_next_time())
                log_task_record(task=task, action="success", now=self.get_next_time())

        elif request.param == "last line fail":
            log_task_record(task=tasks[0], action="run", now=self.get_next_time())
            log_task_record(task=tasks[0], action="success", now=self.get_next_time())

            log_task_record(task=tasks[1], action="run", now=self.get_next_time())
            log_task_record(task=tasks[1], action="fail", now=self.get_next_time())

        elif request.param == "last line last unrun":
            for task in tasks[:-1]:
                # All success but last
                log_task_record(task=task, action="run", now=self.get_next_time())
                log_task_record(task=task, action="success", now=self.get_next_time())

        elif request.param == "last line last fail":
            for task in tasks[:-1]:
                # All but last success
                log_task_record(task=task, action="run", now=self.get_next_time())
                log_task_record(task=task, action="success", now=self.get_next_time())

            log_task_record(task=tasks[-1], action="run", now=self.get_next_time())
            log_task_record(task=tasks[-1], action="fail", now=self.get_next_time())

        else:
            raise ValueError(f"Invalid param value: {request.param}")
        return tasks


class SequenceBase(PipingBase):

    def test_runnable_first(self, sequence, tasks, mock_datetime_now):
        mock_datetime_now("2021-06-01 10:00:00")
        assert bool(tasks[0])
        for task in tasks[1:]:
            assert not bool(task)

    def test_runnable_second(self, sequence, tasks, mock_datetime_now):
        log_task_record(task=tasks[0], action="run", now="2021-06-01 09:30:00")
        log_task_record(task=tasks[0], action="success", now="2021-06-01 09:30:00")
        mock_datetime_now("2021-06-01 10:00:00")
        assert not bool(tasks[0])
        assert bool(tasks[1])
        for task in tasks[2:]:
            assert not bool(task)
        
    def test_runnable_third(self, sequence, tasks, mock_datetime_now):
        # Test third task just in case 
        log_task_record(task=tasks[0], action="run", now="2021-06-01 09:30:00")
        log_task_record(task=tasks[0], action="success", now="2021-06-01 09:30:00")
        mock_datetime_now("2021-06-01 10:00:00")
        log_task_record(task=tasks[1], action="run", now="2021-06-01 09:31:00")
        log_task_record(task=tasks[1], action="success", now="2021-06-01 09:32:00")
        mock_datetime_now("2021-06-01 10:03:00")

        assert not bool(tasks[0])
        assert not bool(tasks[1])
        assert bool(tasks[2])
        for task in tasks[3:]:
            assert not bool(task)

    def test_running(self, sequence, tasks, mock_datetime_now):
        log_task_record(task=tasks[0], action="run", now="2021-06-01 09:30:00")

        mock_datetime_now("2021-06-01 10:00:00")
        for task in tasks:
            assert not bool(task)


@pytest.mark.parametrize("tasks", ["no previous runs", "last line success", "last line fail", "last line last unrun", "last line last fail"], indirect=True)
class TestWithInterval(SequenceBase):

    @pytest.fixture
    def sequence(self, tasks, mock_datetime_now):
        mock_datetime_now("2021-06-01 00:00:00")
        return Sequence(tasks=[task.name for task in tasks], interval="time of day between 09:00 and 17:00")

    def test_before_start(self, sequence, tasks, mock_datetime_now):
        mock_datetime_now("2021-06-01 00:00:00")
        assert not bool(tasks[0])
        assert not bool(tasks[1])


@pytest.mark.parametrize("tasks", ["no previous runs", "last line success", "last line fail", "last line last fail"], indirect=True) # , "last unrun"
class TestWithoutInterval(SequenceBase):

    @pytest.fixture
    def sequence(self, tasks, mock_datetime_now):
        mock_datetime_now("2021-06-01 00:00:00")
        return Sequence(tasks=[task.name for task in tasks])

    def test_first_runnable(self, sequence, tasks, mock_datetime_now):
        mock_datetime_now("2021-06-01 00:00:00")
        assert bool(tasks[0])
        assert not bool(tasks[1])


# Other related tests

@pytest.mark.parametrize("get_pipe", [
    pytest.param(
        lambda: Sequence(tasks=["task1", "task2"], interval="time of day between 10:00 and 16:00"),
        id="With interval",
    ),
    pytest.param(
        lambda: Sequence(tasks=["task1", "task2"]),
        id="Without interval",
    ),
])
def test_sequence_wait_task(session, get_pipe, mock_datetime_now):
    task1 = FuncTask(lambda: None, name="task1", start_cond="time of day between 11:00 and 16:00")
    task2 = FuncTask(lambda: None, name="task2")

    seq = get_pipe()

    assert isinstance(task1.start_cond, All)
    assert task1.start_cond[0] == parse_condition_string("time of day between 11:00 and 16:00")

    mock_datetime_now("2021-06-01 09:00:00")
    assert not bool(task1)
