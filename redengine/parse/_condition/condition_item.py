
from typing import Callable, Dict, Pattern, Union

from ..utils import ParserError, CondParser
from redengine.core.condition.base import PARSERS, BaseCondition
from redengine.session import Session

CONDITION_PARSERS = []

def add_condition_parser(d: Dict[Union[str, Pattern], Union[Callable, 'BaseCondition']]):
    """Add a parsing instruction to be used for parsing a 
    string to condition.

    Parameters
    ----------
    d : dict
        TODO
    """
    parsers = Session._cond_parsers #! TODO
    parsers.update(d)

def parse_condition_item(s:str) -> BaseCondition:
    "Parse one condition"

    session = Session.session

    for statement, parser in session.cond_parsers.items():
        if isinstance(statement, Pattern):
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
        if isinstance(parser, CondParser):
            return parser(s, **kwargs)
        cond = parser(**kwargs)
        return cond
