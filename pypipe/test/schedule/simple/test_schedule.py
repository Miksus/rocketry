
from pypipe import Scheduler

def myfunc():
    print("The task is running")

def test_simple():
    scheduler = Scheduler(
        [
            Task(myfunc, )
        ]
    )

    scheduler()