
# Add arguments here that you wish
# to pass as function arguments to
# the tasks.

from redengine.arguments import FuncArg

@FuncArg.to_session()
def my_session_arg():
    ...
    return 'a session arg'