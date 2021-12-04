
from typing import Pattern

from ..utils import ParserError
from redengine.core.time.base import PARSERS, TimePeriod
from redengine._session import Session

def parse_time_item(s:str):
    "Parse one condition"
    parsers = Session.session.time_parsers
    for statement, parser in parsers.items():
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

    if isinstance(parser, TimePeriod):
        return parser
    else:
        return parser(**kwargs)
