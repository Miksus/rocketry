# This file contains a working scheduling
# system.

from redengine import Session
from redengine.tasks import FuncTask

session = Session(
    scheme=["log_memory"] # Logging to memory
)

# Tasks
# -----

@FuncTask(start_cond="daily")
def my_task_1():
    # Runs once a day
    ...

@FuncTask(start_cond="every 10 min 20 sec")
def my_task_2():
    # Runs once every 10 minutes and 20 seconds
    ...

@FuncTask(start_cond="after task 'my_task_1' & after task 'my_task_2'")
def my_task_3():
    # Runs after "my_task_1" and "my_task_2" succeeded
    ...

if __name__ == "__main__":
    session.start()
    # Blocked till interupted