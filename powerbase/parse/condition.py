
from powerbase.core.condition.base import CLS_CONDITIONS
from ._condition import parse_condition_string

from .utils import ParserPicker, DictInstanceParser

def _parse_condition_string(s:str, **kwargs):
    cond = parse_condition_string(s)
    cond._str = s
    return cond

parse_condition = ParserPicker(
    {
        str: _parse_condition_string,
        dict: DictInstanceParser(classes=CLS_CONDITIONS),
    }
) 