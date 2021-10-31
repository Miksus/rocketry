# This file contains a working scheduling
# system.

from redengine import Session
from redengine.tasks import FuncTask

# Session
# -------

session = Session(
    scheme=["log_memory"] # Logging to memory
)

# Tasks
# -----

@FuncTask(start_cond="minutely")
def my_task_1():
    # Runs once a minute
    ...

@FuncTask(start_cond="daily")
def my_task_2():
    # Runs once a day
    ...

@FuncTask(start_cond="after task 'my_task_2'")
def my_task_3():
    # Runs after "my_task_2" succeeded
    ...


# Starting up
# -----------
if __name__ == "__main__":
    session.start()