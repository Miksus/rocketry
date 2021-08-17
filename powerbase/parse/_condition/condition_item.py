


import re
from typing import Callable

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, expr, parser, regex=True):
        self.expr = expr
        self.parser = parser
        self.regex = regex

    def __call__(self, s):
        if self.regex:
            regex = self.expr
            res = re.fullmatch(regex, s, flags=re.IGNORECASE)
            if res:
                return self.parser(**res.groupdict())
        else:
            if s == self.expr:
                return self.parser(s)
        raise ParserError(f"Could not parse string {repr(s)}.")

CONDITION_PARSERS = []

def add_condition_parser(s:str, func:Callable, regex:bool=True):
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
    CONDITION_PARSERS.append(sentence)

def parse_condition_item(s:str):
    "Parse one condition"
    for parser in CONDITION_PARSERS:
        try:
            return parser(s)
        except ParserError:
            pass
    raise ValueError(f"Cannot parse the condition: {repr(s)}")

