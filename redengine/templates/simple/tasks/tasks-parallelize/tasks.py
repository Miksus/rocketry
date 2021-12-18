
from redengine.tasks import FuncTask

# These are some examples of parallelized tasks

@FuncTask(start_cond='minutely', execution='main')
def task_running_in_main():
    print("Running in main process and thread")
    ...

@FuncTask(start_cond='minutely', execution='thread')
def task_running_in_thread():
    print("Running in child thread")
    ...

@FuncTask(start_cond='minutely', execution='process')
def task_running_in_process():
    print("Running in child process")
    ...
