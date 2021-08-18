
#from powerbase.core.time.base import CLS
from ._time import parse_time_string

from .utils import ParserPicker, DictInstanceParser

def _parse_time_string(s:str):
    time = parse_time_string(s)
    time._str = s
    return time

parse_time = ParserPicker(
    {
        str: _parse_time_string,
        #dict: DictInstanceParser(classes=CLS_CONDITIONS),
    }
) 