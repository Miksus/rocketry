
from redengine.core import parameters
from redengine.tasks import FuncTask
from tasks.settings import my_setting

# These are some examples of parallelized tasks

@FuncTask(start_cond='minutely', parameters={'myparam': 'x'})
def use_specific_parameters(myparam):
    ... # Note: myparam's value is always 'x'

@FuncTask(start_cond='minutely')
def use_session_parameters(email_list):
    ... # See file 'parameters.py'

@FuncTask(start_cond='minutely')
def use_imported():
    ...
    # You can also just import settings, like connections, and use them
    my_setting + " appended"