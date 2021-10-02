
# This file contains a whole scheduling
# system. Useful for simple or quick projects.

from redengine import Session
from redengine.tasks import FuncTask
from redengine.arguments import FuncArg
from redengine.extensions import Sequence

# Session
# -------

session = Session()

# Tasks
# -----

@FuncTask(start_cond="minutely")
def my_pytask_1():
    print(f"Executing 'my_pytask_1'...")
    ...

@FuncTask(start_cond="minutely", execution="main", name="my_pytask_2")
def my_pytask_2(my_session_arg):
    print(f"Executing 'my_pytask_2' with param '{my_session_arg}'...")
    ...

@FuncTask(start_cond="minutely", execution="process", name="my_pytask_3", parameters={"my_param": "a task arg"})
def do_stuff(my_param):
    print(f"Executing 'my_pytask_3' with param '{my_param}'...")
    ...

# Arguments
# ---------

@FuncArg.to_session()
def my_session_arg():
    ...
    return 'a session arg'

# Pipelines
# ---------

Sequence(["my_pytask_2", "my_pytask_3"], interval="every 10 seconds")

# Starting up
# -----------
if __name__ == "__main__":
    session.start()