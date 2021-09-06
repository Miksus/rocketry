
import inspect
from functools import wraps

def set_arguments_as_attributes(init):
    arg_names = inspect.getargspec(init)[0]

    @wraps(init)
    def new_init(self, *args):
        for name, value in zip(arg_names[1:], args):
            setattr(self, name, value)
        init(self, *args)

    return new_init
