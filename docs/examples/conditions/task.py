from redengine.tasks import FuncTask

@FuncTask(start_cond="true")
def task_simple_1():
    "This runs always (just a an example for first one)"
    ...

@FuncTask(start_cond="after task 'task_simple_1'")
def task_simple_2():
    """This runs once after task_simple_1 succeeded 
    before this task"""
    ...

@FuncTask(start_cond="after task 'task_simple_1' succeeded")
def task_simple_3():
    """This also runs once after task_simple_1 succeeded 
    before this task"""
    ...

@FuncTask(start_cond="after task 'task_simple_1' failed")
def task_simple_4():
    """This runs once after task_simple_1 failed
    before this task"""
    ...

@FuncTask(start_cond="task 'task_simple_1' is running")
def task_simple_5():
    """This runs when task_simple_1 is also running
    before this task"""
    ...

# Piping
# ------

@FuncTask(start_cond="""
    after task 'task_simple_1'
    & after task 'task_simple_2'
""")
def task_pipe_1():
    """This runs after task_simple_1 and task_simple_2 have 
    succeeded before this task"""
    ...

@FuncTask(start_cond="""
    after task 'task_simple_1'
    | after task 'task_simple_2'
""")
def task_pipe_2():
    """This runs after either task_simple_1 or task_simple_2 have 
    succeeded before this task"""
    ...

# More complex
# ------------

@FuncTask(start_cond="""
    after task 'task_simple_1'
    & task 'task_simple_2' has failed today
""")
def task_complex_1():
    """This runs after task_simple_1 has succeeded 
    before this task but only if task_simple_2 has failed today"""
    ...

@FuncTask(start_cond="""
    after task 'task_simple_1'
    & task 'task_simple_2' has succeeded today before 10:00
""")
def task_complex_2():
    """This runs after task_simple_1 has succeeded 
    before this task but but only if task_simple_2 has also 
    succeeded today before 10 AM"""
    ...