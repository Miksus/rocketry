from rocketry.conditions import Any, All, Not
from ..utils.string_parser import InstructionParser
from .condition_item import parse_condition_item

def _flatten(*args, types, with_attr):
    comps = []
    for arg in args:
        if isinstance(arg, types):
            comps += getattr(arg, with_attr)
        else:
            comps.append(arg)
    return comps
def _parse_any(*args):
    comps = _flatten(*args, types=Any, with_attr="subconditions")
    return Any(*comps)

def _parse_all(*args):
    comps = _flatten(*args, types=All, with_attr="subconditions")
    return All(*comps)

def _parse_not(arg):
    if hasattr(arg, "__invert__"):
        return ~arg
    if isinstance(arg, Not):
        return ~arg
    return Not(arg)

parse_condition_string = InstructionParser(
    parse_condition_item,
    operators=[
        {
            "symbol": "~",
            "func": _parse_not,
            "side": "right",
        },
        {
            "symbol": "&",
            "func": _parse_all,
            "side": "both",
        },
        {
            "symbol": "|",
            "func": _parse_any,
            "side": "both",
        },
    ]
)
