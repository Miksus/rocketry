
import logging
import warnings
import datetime
from typing import TYPE_CHECKING, Iterable, List, Dict, Union

from dateutil.parser import parse as _parse_datetime
import pandas as pd

from redengine.core.utils import is_main_subprocess

if TYPE_CHECKING:
    from redengine.core import Task

class TaskAdapter(logging.LoggerAdapter):
    """Logging adapter for tasks.

    The adapter includes the name of the given 
    task to the log records and allows reading
    the log records if a handler with reading
    capability is found.

    Parameters
    ----------
    logger : logging.Logger
        Logger the TaskAdapter is for.
    task : Task, str
        Task the adapter is for.
    """
    def __init__(self, logger:logging.Logger, task:Union['Task', str]):
        task_name = task.name if hasattr(task, 'name') else task
        super().__init__(logger, {"task_name": task_name})

        is_readable = any(
            hasattr(handler, "read") or hasattr(handler, "query")
            for handler in self.logger.handlers
        )
        is_process_dummy = logger.name.endswith("_process")
        if not is_readable and not is_process_dummy and is_main_subprocess():
            warnings.warn(f"Logger '{logger.name}' for task '{self.task_name}' does not have ability to be read. Past history of the task cannot be utilized.")

    def process(self, msg, kwargs):
        ""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs

    def get_records(self, **kwargs) -> Iterable[Dict]:
        r"""Get the log records of the task from the 
        handlers of the logger.
        
        One of the handlers in the logger must 
        have one of the methods:

        - read()
        - query(\*\*kwargs)

        Parameters
        ----------
        **kwargs : dict
            Query arguments to filter the log records.

        """
        # TODO: Add examples in docstring

        task_name = self.extra["task_name"]
        handlers = self.logger.handlers

        if task_name is not None:
            kwargs["task_name"] = task_name

        for handler in handlers:
            if hasattr(handler, "query"):
                records = handler.query(
                    **kwargs
                )
                formatter = RecordFormatter()
                for record in formatter(records):
                    yield record
                break
            elif hasattr(handler, "read"):

                formatter = RecordFormatter()
                filter = RecordFilter(kwargs)

                records = filter(formatter(handler.read()))
                yield from records
                break
        else:
            raise AttributeError(f"Logger '{self.logger.name}' cannot be read. Missing readable handler.")

    def get_latest(self, action:str=None) -> dict:
        """Get latest log record. Note that this
        is in the same order as in which the 
        handler(s) return the log records.
        
        Parameters
        ----------
        action : str
            Filtering with latest action of this
            type.
        """
        record = {}
        for record in self.get_records(action=action):
            pass # Iterating the generator till the end
        return record

# For some reason the logging.Adapter is missing some
# methods that are on logging.Logger
    def handle(self, *args, **kwargs):
        "See `Logger.handle <https://docs.python.org/3/library/logging.html#logging.Logger.handle>`_"
        return self.logger.handle(*args, **kwargs)

    def addHandler(self, *args, **kwargs):
        "See `Logger.addHandler <https://docs.python.org/3/library/logging.html#logging.Logger.addHandler>`_"
        return self.logger.addHandler(*args, **kwargs)

    def __eq__(self, o: object) -> bool:
        is_same_type = type(self) == type(o)
        has_same_logger = self.logger == o.logger
        has_same_name = self.name == o.name
        return is_same_type and has_same_logger and has_same_name

    @property
    def task_name(self):
        return self.extra['task_name']

# Utils
def parse_datetime(dt):
    return _parse_datetime(dt) if not isinstance(dt, (datetime.datetime, pd.Timestamp)) and dt is not None else dt

class RecordFormatter:

    def __call__(self, data:List[Union[Dict, logging.LogRecord]]):
        for record in data:
            if isinstance(record, logging.LogRecord):
                # Turn the LogRecord to dict
                record = vars(record)
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