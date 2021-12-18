
# This file contains a whole scheduling
# system. Useful for simple or quick projects.

from redengine import session

from redengine.tasks import FuncTask
from redengine.parameters import FuncParam
from redengine.conditions import FuncCond
from redengine.arguments import Return


# Session
# -------

session.set_scheme("log_simple") # Logging to memory, customize as needed.


# Custom Conditions
# -----------------

@FuncCond(syntax="is foo")
def is_foo():
    ...
    return True


# Parameters
# ----------

@FuncParam()
def email_list():
    ...
    return ['me', 'you']


# Tasks
# -----

# Feel free to delete/modify as you wish.

@FuncTask(start_cond="minutely")
def task_1():
    ...

@FuncTask(start_cond="daily", execution="thread", name="first_task")
def task_2(email_list):
    ... # Note: email_list is a session parameter

@FuncTask(start_cond="after task 'first_task'", parameters={"param_1": Return("first_task")})
def task_3(param_1):
    ...

@FuncTask(start_cond="is foo & daily after 08:00")
def task_4():
    ...


# Starting up
# -----------
if __name__ == "__main__":
    session.start()