
import logging
import csv
import io
import os
from logging import Formatter, FileHandler, Handler, LogRecord
from pathlib import Path
from typing import List, Dict
from dateutil.parser import parse as parse_datetime

class AttributeFormatter(Formatter):
    """Formatter but instead of generating a string,
    the logging items are set to the record for the 
    handler to use.
    """

    def __init__(self, *args, has_default=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_default = has_default

    def format(self, record:LogRecord) -> LogRecord:

        # We copy Formatter.format but put those to the record 
        # instead to the returned message
        record.message = record.getMessage()

        self.set_exc_text(record)
        self.set_stack_text(record)
        self.set_traceback(record)
        self.set_formatted_message(record)


        return record

    def set_formatted_message(self, record:LogRecord):
        s = self.formatMessage(record)
        if hasattr(record, 'traceback') and record.traceback:
            s = self._add_new_line(s) + record.traceback
        record.formatted_message = s

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
        

class MemoryHandler(Handler):
    """[summary]
    """
    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, store_as="record", **kwargs):
        """
        Open the specified file and use it as the stream for logging.
        """
        super().__init__(**kwargs)
        self.records = []
        self.store_as = store_as
        
    def emit(self, record:logging.LogRecord):
        msg = self.format(record)

        if self.store_as == "record":
            self.records.append(record)
        elif self.store_as == "dict":
            self.records.append(vars(record))
        else:
            raise ValueError(f"Invalid value: {self.store_as}")

# Extras
    def read(self, **kwargs) -> List[Dict]:
        "Read the log file as pandas dataframe"
        yield from self.records
        
    def clear_log(self):
        "Empty the logging file"
        self.close()
        file = self.baseFilename
        with open(file, "w") as f:
            pass
        self.write_headers()
