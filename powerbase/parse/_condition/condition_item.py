


import re
from typing import Callable, Dict, Optional, Pattern, Union
from ..utils import Parser, ParserError
from powerbase.core.condition.base import PARSERS, BaseCondition

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task


CONDITION_PARSERS = []

def add_condition_parser(d: Dict[Union[str, Pattern], Union[Callable, 'BaseCondition']]):
    """Add a parsing instruction to be used for parsing a 
    string to condition.

    Parameters
    ----------
    d : dict
        TODO
    """
    PARSERS.update(d)

def parse_condition_item(s:str) -> BaseCondition:
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

    if isinstance(parser, BaseCondition):
        return parser
    else:
        return parser(**kwargs)

