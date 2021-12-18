
import re
from redengine.conditions import FuncCond

@FuncCond(syntax='is foo')
def is_foo():
    ... # Use this in start_cond like 'is foo'
    return True

@FuncCond(syntax=re.compile('is bar at (?P<place>.+)'))
def is_foo(place):
    ... # Use this in start_cond like 'is bar at home'
    return True