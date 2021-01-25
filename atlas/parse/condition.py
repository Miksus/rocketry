


import re



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
        raise ParserError

CONDITION_PARSERS = []

def add_condition_parser(s, func, regex=True):
    sentence = Parser(s, func, regex=regex)
    CONDITION_PARSERS.append(sentence)

def parse_condition(s:str):
    "Parse one condition"
    for parser in CONDITION_PARSERS:
        try:
            return parser(s)
        except ParserError:
            pass
    raise ValueError(f"Cannot parse statement: {s}")

