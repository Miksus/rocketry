
# Note: this import is from the task root
# directory.
from tasks.settings import my_setting

def do_things():
    print(f"Doing things with {my_setting}")
    ...

def main(my_task_param, my_session_arg):
    # NOTE: argument 'my_task_param' comes from 
    # the task configuration and 'my_param' from
    # the session parameters.
    print(f"Executing funcs.py 'main' with param {my_task_param} and {my_session_arg}")
    ...