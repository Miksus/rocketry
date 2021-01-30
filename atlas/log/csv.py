
import logging
import csv
import io
import os
from logging import Formatter, FileHandler
from pathlib import Path

class CsvFormatter(Formatter):
    # https://stackoverflow.com/a/19766056
    """
    Format the output as row in csv file
    """
    fields = [
        "levelname",
        "asctime",
        "msg",
    ]
    
    
    def __init__(self, fields=None, **kwargs):
        super().__init__()
        self._output = io.StringIO()
        self.csv_kwargs = kwargs
        self.fields = fields if fields is not None else self.fields

    def format(self, record):
        # Copied from: https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L674
        super().format(record)
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
        

class CsvHandler(FileHandler):
    """[summary]

    Usage:
    ------
        logging.basicConfig(level=logging.DEBUG)

        logger = logging.getLogger(__name__)
        logger.addHandler(
            CsvHandler(
                "log.csv", 
                headers=["time", "level", "message"],
                fields=["asctime", "levelname", "msg"], 
                kwds_csv=dict(delimiter=";")
            )
        )
    """
    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, filename, *args, delay=False, headers=None, kwds_csv=None, make_dir=False, **kwargs):
        """
        Open the specified file and use it as the stream for logging.
        """
        if make_dir and not delay:
            # We need to create the dir before opening
            # the stream
            self.create_dir()

        super().__init__(filename, *args, delay=delay, **kwargs)
        
        kwds_csv = kwds_csv or {}
        
        self.headers = headers
        self.make_dir = make_dir

        if not delay:
            self.write_headers()
        
    def format(self, record):
        return self.formatter.format(record)
        
    def emit(self, record):

        delay = True if self.stream is None else None

        # We need to create the dir before opening 
        # the stream (if asked)
        if delay and self.make_dir:
            self.create_dir()

        if delay:
            # We open the stream for Filehandler.emit
            # as the headers should be written
            # before the row
            # https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L1201
            self.stream = self._open()
            self.write_headers()

        super().emit(record)

    def create_dir(self):
        "Create directory where the log file is"
        filename = self.baseFilename
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

    def write_headers(self):
        file = self.baseFilename
        headers = self.headers

        header_str = self.formatter.to_row(headers)
        if os.path.getsize(file) == 0:
            # If the file is empty, it must miss headers
            # thus made
            with open(file, "a") as f:
                f.write(header_str + "\n")
                
        # Deleting _writer in case the handler/formatter
        # is to be deepcopied (writer cannot be pickled)
        # The _writer attribute is regenerated
        del self.formatter._writer
                
# Extras
    def read(self, **kwargs):
        "Read the log file as pandas dataframe"
        import pandas as pd
        dt_cols = (
            [self.formatter.fields.index("asctime")]
            if "asctime" in self.formatter.fields 
            else None
        )
        parse_dates = kwargs.pop("parse_dates", dt_cols)
        if not Path(self.baseFilename).exists():
            return pd.DataFrame(columns=self.headers)
        return pd.read_csv(self.baseFilename, parse_dates=parse_dates, dialect=self.formatter.writer.dialect, **kwargs)

    def clear_log(self):
        "Empty the logging file"
        self.close()
        file = self.baseFilename
        with open(file, "w") as f:
            pass
        self.write_headers()

    @property
    def headers(self):
        return self.formatter.fields if self._headers is None else self._headers

    @headers.setter
    def headers(self, val):
        self._headers = val