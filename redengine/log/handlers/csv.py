
import csv
import os
from logging import FileHandler
from pathlib import Path
from typing import List, Dict

from ..formatters import CsvFormatter


class CsvHandler(FileHandler):
    """A handler class which writes the log records
    to a CSV file in which the records can be read.

    A subclass of `logging.FileHandler <https://docs.python.org/3/library/logging.handlers.html#filehandler>`_.

    Parameters
    ----------
    filename : path-like
        CSV file used for writing the records.
    delay : bool
        If True, the CSV file and the headers
        are created and opened when the handler 
        is first time used. Otherwise these are
        done at the creation of the handler, 
        by default True
    fields : list
        List of attributes in logging.LogRecord
        which are written in this order to the CSV
        file. By default, uses CsvFormatter.fields
    headers : list
        Names of the columns/headers in the CSV
        file. Should have same length as the fields.
        By default uses the names of the fields.
    kwds_csv : dict
        Keyword arguments for 
    make_dir : bool
        If True, the directory where the CSV file
        is, is also created, by default False
    *args : tuple
        See `logging.FileHandler <https://docs.python.org/3/library/logging.handlers.html#filehandler>`_
    **kwargs : tuple
        See `logging.FileHandler <https://docs.python.org/3/library/logging.handlers.html#filehandler>`_


    Examples
    --------

    >>> from redengine.log import CsvHandler
    >>> handler = CsvHandler(
    ...     'logfile.csv', 
    ...     fields=['asctime', 'message', 'level'], 
    ...     headers=['timestamp', 'log_message', 'log_level']
    ... ) # doctest: +SKIP
    """

    default_formatter = CsvFormatter()

    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, filename, *args, delay=True, fields=None, headers=None, kwds_csv=None, make_dir=False, **kwargs):
        if make_dir and not delay:
            # We need to create the dir before opening
            # the stream
            self.create_dir()

        super().__init__(filename, *args, delay=delay, **kwargs)
        if not self.formatter:
            # Formatter was not passed with __init__, we set default
            self.formatter = CsvFormatter(fields=fields)
        
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
        "Create directory where the log file is."
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
    def read(self, **kwargs) -> List[Dict]:
        "Read the log file"
        # We return generator to be more performant
        if not Path(self.baseFilename).exists():
            return []
        #data = []
        columns = self.formatter.fields 
        with open(self.baseFilename, "r") as file:
            reader = csv.reader(file, dialect=self.formatter.writer.dialect)

            # headers
            columns = next(reader, None)
            for row in reader:
                row_dict = dict(zip(columns, row))
                yield row_dict

                #data.append(row_dict)

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