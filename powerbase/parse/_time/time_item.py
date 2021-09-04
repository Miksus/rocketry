


import re
from typing import Callable
from ..utils import Parser, ParserError
from powerbase.core.time.base import PARSERS, TimePeriod

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task



from ..utils import Parser, ParserError

def add_time_parser(d):
    """Add a parsing instruction to be used for parsing a 
    string to condition.

    Parameters
    ----------
    s : str
        Exact string (if regex=False) or regex (if regex=True)
        to be matched. If regex and has groups, the groups are
        passed to func.
    func : Callable
        Function that should return a condition. 
    regex : bool, optional
        Whether the 's' is a regex or exact string, 
        by default True
    """
    PARSERS.update(d)

def parse_time_item(s:str):
    "Parse one condition"
    for statement, parser in PARSERS.items():
        if isinstance(statement, re.Pattern):
            res = statement.fullmatch(s)
            if res:
                args = ()
                kwargs = res.groupdict()
                break
        else:
            if s == statement:
                args = (s,)
                kwargs = {}
                break
    else:
        raise ParserError(f"Could not find parser for string {repr(s)}.")

    if isinstance(parser, TimePeriod):
        return parser
    else:
        return parser(**kwargs)
