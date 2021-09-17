
from logging import Formatter, LogRecord

import csv
import io
from logging import Formatter
from typing import Callable, Dict, List

class AttributeFormatter(Formatter):
    """Format the log record to a row 
    in CSV file.

    Parameters
    ----------
    has_default : bool
        If True, adds the exception attributes
        with None if no exceptions.
    include : List[str]
        List of attribute names that are filtered.
    exclude : List[str]
        List of attribute names that are fitered out. 
    attr_formats : Dict[str, Callable]
        Dictionary of function for formatting the 
        attribute values.
    *args : tuple
        See `logging.Formatter <https://docs.python.org/3/library/logging.html#formatter-objects>`_
    **kwargs : tuple
        See `logging.Formatter <https://docs.python.org/3/library/logging.html#formatter-objects>`_


    """

    def __init__(self, *args, has_default:bool=False, include:List[str]=None, exclude:List[str]=None, attr_formats:Dict[str, Callable]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_default = has_default
        self.include = include
        self.exclude = exclude
        self.attr_formats = attr_formats

    def format(self, record:LogRecord) -> LogRecord:

        # We copy Formatter.format but put those to the record 
        # instead to the returned message
        record.message = record.getMessage()

        self.set_exc_text(record)
        self.set_stack_text(record)
        self.set_traceback(record)
        self.set_formatted_message(record)

        self.prune(record)
        self.format_attrs(record)
        return record

    def prune(self, record:LogRecord):
        if self.include:
            attrs = list(vars(record))
            for attr in attrs:
                if attr not in self.include:
                    delattr(record, attr)
        if self.exclude:
            for attr in self.exclude:
                if hasattr(record, attr):
                    delattr(record, attr)

    def format_attrs(self, record:LogRecord):
        if self.attr_formats:
            for attr, func in self.attr_formats.items():
                if hasattr(record, attr):
                    setattr(record, attr, func(getattr(record, attr)))

    def set_formatted_message(self, record:LogRecord):
        s = self.formatMessage(record)
        if hasattr(record, 'traceback') and record.traceback:
            s = self._add_new_line(s) + record.traceback
        record.message = s

    def set_exc_text(self, record:LogRecord):
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

    def set_stack_text(self, record:LogRecord):
        if record.stack_info:
            record.stack_text = self.formatStack(record.stack_info)
        elif self.has_default:
            record.stack_text = None

    def set_traceback(self, record:LogRecord):
        if record.stack_info and not hasattr(record, "stack_text"):
            self.set_stack_text(record)
        if record.exc_text and hasattr(self, "stack_text"):
            record.traceback = self._add_new_line(record.exc_text) + record.stack_text
        elif self.has_default:
            record.traceback = None

    def _add_new_line(self, s:str):
        return s if s[-1] == "\n" else s + '\n'
        