
from pypipe import Scheduler, Task
from pypipe.conditions import scheduler_cycles

Task.use_instance_naming = True

def myfunc():
    print("The task is running")

def failing():
    raise TypeError("Failed task")

def succeeding():
    print("Success")

def test_simple(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        task_success = Task(succeeding)
        task_fail = Task(failing)
        scheduler = Scheduler(
            [
                task_success,
                task_fail
            ], shut_condition=scheduler_cycles >= 3
        )
        
        scheduler()

        history = task_success.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_fail.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 3 == (history["action"] == "fail").sum()


def test_dependent(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        task_success = Task(succeeding, name="first")
        task_fail = Task(failing, dependent="succeeding")
        scheduler = Scheduler(
            [
                task_success,
                task_fail
            ], shut_condition=scheduler_cycles >= 1
        )
        
        scheduler()

        history = task_success.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_fail.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 3 == (history["action"] == "fail").sum()