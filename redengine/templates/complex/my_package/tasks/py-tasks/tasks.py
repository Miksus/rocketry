
# You can also load tasks with
# PyLoader that simply loads all
# Python files fulfilling the given
# file pattern.

# The tasks are generated once on 
# import thus be aware of syntax
# errors. 

# Also make sure the session is 
# correct as the loader is not aware 
# of the content of this file.

from redengine.tasks import FuncTask
from redengine.extensions import Sequence


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


# Sequences (pipelines)
# ---------------------

# These are task pipelines: a task can run only
# when the previous task has succeeded. The first
# task in the pipeline can only run when the 
# interval is met or when the last task has succeeded
# if interval is not defined.

# The pipe starts every 10 seconds: every 10 seconds 
# both of these are allowed to run once and they must
# run in the specified order.
Sequence(
    ["my_pytask_2", "my_pytask_3"],
    interval="every 10 seconds"
)