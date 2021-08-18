
import re
from .exception import ParserError

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