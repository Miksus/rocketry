
# Extensions for tasks
import re
from powerbase.core import BaseCondition

class MyCondition(BaseCondition):
    """My condition class"""
    __parsers__ = {
        re.compile("is mycond in effect"): "__init__"
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __bool__(self, *args, **kwargs):
        # Whether the condition is True or False
        return True