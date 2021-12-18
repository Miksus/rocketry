
# Put your tasks here

from redengine.core import parameters
from redengine.tasks import FuncTask
from redengine.arguments import Return

# These are some examples of piping tasks

@FuncTask(start_cond="minutely", name="pipe_task_1")
def pipe_task_1():
    print("Executing 'pipe_task_1'...")
    ...
    return 'x'

@FuncTask(start_cond="after task 'pipe_task_1'", parameters={'param_1': Return('pipe_task_1')}, name="pipe_task_2")
def pipe_task_2(param_1):
    print("Executing 'pipe_task_2'")
    ...
    return 'y'

@FuncTask(
    start_cond="after tasks 'pipe_task_1', 'pipe_task_2'", 
    parameters={"param_1": Return('pipe_task_1'), "param_2": Return('pipe_task_2')}, 
)
def pipe_task_3(param_1, param_2):
    print("Executing 'pipe_task_3'")
    ...
