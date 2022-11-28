from .base import (All, Any, Equal, Greater, GreaterEqual, Key, Less,  # Query,
                   LessEqual, Not, NotEqual)
from .parse import Parser
from .string import Regex

parser = Parser()
from_dict_string = parser.from_dict
