
import logging
import warnings

import pandas as pd
from typing import List, Dict
from dateutil.parser import parse as parse_datetime

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
        task_name = task.name if task is not None else task
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

                filter = RecordFilter(kwargs)

                records = filter(handler.read())
                for record in records:
                    # TODO 
                    for dt_key in ("start", "end", "asctime"):
                        if dt_key in record and record[dt_key]:
                            record[dt_key] = parse_datetime(record[dt_key])
                    yield record
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
class RecordFilter:
    def __init__(self, query:dict):
        self.query = query

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
                if type(value)(record_value) != value:
                    break
            elif is_range:
                # Considered as range
                start, end = value[0], value[1]

                if start is not None and type(start)(record_value) < start:
                    # Outside of start
                    break
                if end is not None and type(end)(record_value) > end:
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