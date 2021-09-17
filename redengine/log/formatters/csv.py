from logging import Formatter, LogRecord

import csv
import io
from logging import Formatter


class CsvFormatter(Formatter):
    """Format the log record to a row 
    in CSV file.

    Parameters
    ----------
    fields : list
        List of attributes in logging.LogRecord
        which are written in this order to the CSV
        file. 
    **kwargs : dict
        Keyword arguments for csv.writer.
    """
    
    # https://stackoverflow.com/a/19766056
    fields = [
        "asctime",
        "levelname",
        "msg",
        "exc_text",
    ]
    
    def __init__(self, fields=None, **kwargs):
        super().__init__()
        self._output = io.StringIO()
        self.csv_kwargs = kwargs
        self.fields = fields if fields is not None else self.fields

    def format(self, record):
        # Copied from: https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L674
        record.message = super().format(record)
        self.add_extra(record)
        row = self.get_row(record)
        self._rec = record

        return self.to_row(row)

    def usesTime(self):
        return "asctime" in self.fields
    
    def add_extra(self, record):
        # Copied from https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L646
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
    
    def get_row(self, record):
        basic = record.__dict__
        extra = record.args
        if not isinstance(extra, dict):
            extra = {}
        return [extra.get(field, basic.get(field, "")) for field in self.fields]
    
    def to_row(self, row):
        
        self.writer.writerow(row)
        data = self._output.getvalue()
        
        # Flush and reset
        self._output.truncate(0)
        self._output.seek(0)
        return data.strip()
    
    @property
    def writer(self):
        # We create csv writer lazily as
        # pickling is not possible with
        # csv writer. Lazy creation allows
        # to pass this to multiprocess etc.
        # after initiation (but before using)
        if not hasattr(self, "_writer"):
            self._writer = csv.writer(self._output, quoting=csv.QUOTE_ALL, **self.csv_kwargs)
        return self._writer