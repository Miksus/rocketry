
import logging
import warnings
import datetime
import time

import pandas as pd
from typing import List, Dict
from dateutil.parser import parse as _parse_datetime

class TaskAdapter(logging.LoggerAdapter):
    """
    This Logger adapter adds the kwargs 
    from init extras to the kwargs extras.

    One of the handlers must have following method(s):
        - read_as_df : read the log to a pandas dataframe
        - query : 
    
    Usage:
    ------
        logger = logging.getLogger(__name__)
        logger = TaskAdapter(logger, {"task": "mything"})
    """
    def __init__(self, logger, task):
        task_name = task.name if hasattr(task, 'name') else task
        super().__init__(logger, {"task_name": task_name})

        is_readable = any(
            hasattr(handler, "read") or hasattr(handler, "query")
            for handler in self.logger.handlers
        )
        if not is_readable:
            warnings.warn("Task logger does not have ability to be read. Past history of the task cannot be utilized.")


    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs

    def get_records(self, **kwargs) -> List[Dict]:
        """This method is needed for the events to 
        get the run records to determine if the task
        is finished/still running/failed etc. in 
        multiprocessing for example"""

        task_name = self.extra["task_name"]
        handlers = self.logger.handlers

        if task_name is not None:
            kwargs["task_name"] = task_name

        for handler in handlers:
            if hasattr(handler, "query"):
                records = handler.query(
                    **kwargs
                )
                for record in records:
                    yield record
                break
            elif hasattr(handler, "read"):

                formatter = RecordFormatter()
                filter = RecordFilter(kwargs)

                records = filter(formatter(handler.read()))
                yield from records
                break
        else:
            warnings.warn(f"Logger {self.logger.name} is not readable. Cannot get history.")
            return

    def get_latest(self, action=None) -> dict:
        "Get latest log record"
        record = {}
        for record in self.get_records(action=action):
            pass # Iterating the generator till the end
        return record

# For some reason the logging.Adapter is missing some
# methods that are on logging.Logger
    def handle(self, *args, **kwargs):
        return self.logger.handle(*args, **kwargs)

    def addHandler(self, *args, **kwargs):
        return self.logger.addHandler(*args, **kwargs)

    def __eq__(self, o: object) -> bool:
        is_same_type = type(self) == type(o)
        has_same_logger = self.logger == o.logger
        has_same_name = self.name == o.name
        return is_same_type and has_same_logger and has_same_name

class TaskFilter(logging.Filter):
    """Filter only task related so one logger can be
    used with scheduler and tasks"""
    def __init__(self, *args, include, **kwargs):
        super().__init__()
        self.include = include

    def filter(self, record):
        if self.include:
            return hasattr(record, "task")
        else:
            return not hasattr(record, "task")

# Utils
def parse_datetime(dt):
    return _parse_datetime(dt) if not isinstance(dt, (datetime.datetime, pd.Timestamp)) and dt is not None else dt

class RecordFormatter:

    def __call__(self, data:List[Dict]):
        for record in data:
            self.format(record)
            yield record

    def format(self, record:dict):
        self.format_timestamp(record)
        self.format_runtime(record)
        self.format_runstamps(record)

    def format_runstamps(self, record):
        "Format 'start' and 'end' if found"
        for dt_key in ("start", "end"):
            if dt_key in record and record[dt_key]:
                dt_val = record[dt_key]
                if not isinstance(dt_val, datetime.datetime):
                    # This is the situation if reading from file or so
                    record[dt_key] = parse_datetime(record[dt_key])

    def format_runtime(self, record:dict):
        # This is not required
        if "runtime" in record:
            record["runtime"] = pd.Timedelta(record["runtime"])

    def format_timestamp(self, record:dict):
        if "timestamp" in record:
            timestamp = parse_datetime(record['timestamp'])
        elif "created" in record:
            # record.create is in every LogRecord (but not necessarily end up to handler msg)
            created = record["created"]
            timestamp = datetime.datetime.fromtimestamp(float(created))
        elif "asctime" in record:
            # asctime is most likely in handler message when formatted
            asctime = record["asctime"]
            timestamp = parse_datetime(asctime) if not isinstance(asctime, datetime.datetime) else asctime
        else:
            raise KeyError(f"Cannot determine 'timestamp' for record: {record}")
        record["timestamp"] = timestamp

class RecordFilter:

    formats = {
        # From: https://docs.python.org/3/library/logging.html#logrecord-attributes
        "timestamp": parse_datetime,
        "start": parse_datetime,
        "end": parse_datetime,
        "asctime": str,
        "created": float,
        "relativeCreated": int,
        "lineno": int,
        "thread": int,
        "msecs": int,
        "runtime": pd.Timedelta,
    }

    def __init__(self, query:dict):
        self.query = {key: self.format_query_value(val, key) for key, val in query.items()}

    def __call__(self, data:List[Dict]):
        for record in data:
            if self.include_record(record):
                yield record

    def include_record(self, record:dict):
        for key, value in self.query.items():
            if key not in record:
                break
            record_value = record[key]

            is_equal = isinstance(value, str)
            is_range = isinstance(value, tuple) and len(value) == 2
            is_in = isinstance(value, list)
            if is_equal:
                if record_value != value:
                    break
            elif is_range:
                # Considered as range
                start, end = value[0], value[1]

                if start is not None and record_value < start:
                    # Outside of start
                    break
                if end is not None and record_value > end:
                    # Outside of end
                    break
            elif is_in:
                if record_value not in value:
                    # Outside of items
                    break
        else:
            # Loop did not break (no condition violated)
            return True
        # Loop did break, 
        return False

    def format_query_value(self, val, key):
        if isinstance(val, slice):
            val.start = self._format_value(val.start, key=key)
            val.stop = self._format_value(val.stop, key=key)
        elif isinstance(val, list):
            val = [self._format_value(subval, key=key) for subval in val]
        elif isinstance(val, tuple):
            val = tuple(self._format_value(subval, key=key) for subval in val)
        else:
            val = self._format_value(val, key=key)
        return val

    def _format_value(self, val, key):
        if key in self.formats:
            return self.formats[key](val)
        else:
            return val

    def _to_same_type(self, record_value, other):
        if isinstance(other, datetime.datetime):
            return parse_datetime(record_value)
        else:
            return type(other)(record_value)