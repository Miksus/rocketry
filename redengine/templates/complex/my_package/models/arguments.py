
# Extensions for tasks
import re
from redengine.core import Argument

from copy import copy

class MyArgument(Argument):
    """My argument class"""

    def __init__(self, value, **kwargs):
        self.value = value

    def get_value(self, task=None, *args, **kwargs):
        """Get the actual value of the argument.
        Override for custom behaviour."""
        return self.value

    def stage(self, task=None, *args, **kwargs):
        """Get (a copy of) the argument with a 
        value that can be passed to child threads
        or processes. 
        
        Optional."""

        new_self = copy(self)
        new_self.value = ... # Get the staged value
        return new_self

    @classmethod
    def to_session(cls, name:str):
        """Construct MyArgument(s) and put them to
        the session.
        
        Optional."""
        ...
        cls.session.parameters[name] = cls(value)