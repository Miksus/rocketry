
from atlas.core.conditions.base import CLS_CONDITIONS
from ._condition import parse_condition_string

from .utils import ParserPicker, DictInstanceParser

parse_condition = ParserPicker(
    {
        str: parse_condition_string,
        dict: DictInstanceParser(classes=CLS_CONDITIONS),
    }
) 