
# Add arguments here that you wish
# to pass as function arguments to
# the tasks.

from redengine.parameters import FuncParam

@FuncParam('email_list')
def email_list():
    # This is automatically passed to tasks 
    # that require a parameter named email_list
    ... 
    return ['me', 'you']
