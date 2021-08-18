


import re
from typing import Callable

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task



from ..utils import Parser, ParserError

TIME_PARSERS = []

def add_time_parser(s:str, func:Callable, regex:bool=True):
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
    sentence = Parser(s, func, regex=regex)
    TIME_PARSERS.append(sentence)

def parse_time_item(s:str):
    "Parse one condition"
    for parser in TIME_PARSERS:
        try:
            return parser(s)
        except ParserError:
            pass
    raise ValueError(f"Cannot parse the condition: {repr(s)}")

