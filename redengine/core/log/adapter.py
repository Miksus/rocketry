
import logging
import warnings
import datetime
from typing import TYPE_CHECKING, Iterable, List, Dict, Union

from dateutil.parser import parse as _parse_datetime
import pandas as pd

from redengine.core.utils import is_main_subprocess
from redengine.pybox import query

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
    task : redengine.core.Task, str
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

    def get_records(self, qry=None, **kwargs) -> Iterable[Dict]:
        r"""Get the log records of the task from the 
        handlers of the logger.
        
        One of the handlers in the logger must 
        have one of the methods:

        - read()
        - query(qry)

        Parameters
        ----------
        qry : list of tuples, dict, Expression
            Query expression to filter records
        **kwargs : dict
            Keyword arguments turned to a query (if qry is None)

        """
        # TODO: Add examples in docstring

        task_name = self.extra["task_name"]
        handlers = self.logger.handlers

        if task_name is not None:
            kwargs["task_name"] = task_name

        if qry is None:
            qry = query.parser.from_kwargs(**kwargs)
        elif isinstance(qry, list):
            qry = query.parser.from_tuple(qry)
        elif isinstance(qry, dict):
            qry = query.parser.from_dict(qry)
        for handler in handlers:
            if hasattr(handler, "query"):
                records = handler.query(qry)
                formatter = RecordFormatter()
                for record in formatter(records):
                    yield record
                break
            elif hasattr(handler, "read"):

                formatter = RecordFormatter()
                for record in formatter(handler.read()):
                    if qry.match(record):
                        yield record
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
        kwargs = {'action': action} if action is not None else {}
        for record in self.get_records(**kwargs):
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
                record[dt_key] = pd.Timestamp(record[dt_key])

    def format_runtime(self, record:dict):
        # This is not required
        if "runtime" in record:
            record["runtime"] = pd.Timedelta(record["runtime"])

    def format_timestamp(self, record:dict):
        if "timestamp" in record:
            timestamp = pd.Timestamp(record['timestamp'])
        elif "created" in record:
            # record.create is in every LogRecord (but not necessarily end up to handler msg)
            created = record["created"]
            timestamp = pd.Timestamp.fromtimestamp(float(created))
        elif "asctime" in record:
            # asctime is most likely in handler message when formatted
            asctime = record["asctime"]
            timestamp = pd.Timestamp(asctime)
        else:
            raise KeyError(f"Cannot determine 'timestamp' for record: {record}")
        record["timestamp"] = timestamp
