
def do_things():
    print(f"Doing things.")
    ...

def main(my_task_param, my_session_arg):
    # NOTE: argument 'my_task_param' comes from 
    # the task configuration and 'my_param' from
    # the session parameters.
    print(f"Executing funcs.py 'main' with param {my_task_param} and {my_session_arg}")
    ...