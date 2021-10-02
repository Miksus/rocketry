
# Add arguments here that you wish
# to pass as function arguments to
# the tasks.

# Optionally you can use settings.py
# to import relevant variables, classes
# or functions in your tasks to 
# make the parametrization simpler.

from redengine.arguments import FuncArg

@FuncArg.to_session()
def my_session_arg():
    ...
    return 'production server'