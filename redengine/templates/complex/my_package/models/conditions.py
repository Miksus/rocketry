
# Extensions for tasks
import re
from redengine.core import BaseCondition

class MyCondition(BaseCondition):
    """My condition class"""
    __parsers__ = {
        # Parser keys can be regex or just regular strings.
        # The values should be either callables or names of
        # the methods. 
        
        # If regex contains named groups ("(?P<...>...)")
        # the groups are passed as arguments to the constructor.
        re.compile("is mycond (?P<arg>in effect)?"): "__init__",
        "is mycond": "__init__",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __bool__(self, *args, **kwargs):
        """Whether MyCondition is in effect."""
        # Whether the condition is True or False
        return True or False