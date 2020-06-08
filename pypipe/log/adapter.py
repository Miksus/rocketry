
import logging
import warnings

import pandas as pd

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
        super().__init__(logger, {"task_name": task.name})

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

    def get_records(self, start=None, end=None, action=None, **kwargs):
        """This method is needed for the events to 
        get the run records to determine if the task
        is finished/still running/failed etc. in 
        multiprocessing for example"""
        task_name = self.extra["task_name"]
        handlers = self.logger.handlers
        for handler in handlers:
            if hasattr(handler, "query"):
                kwds = {"asctime": (start, end), "action": action, "task_name": task_name}
                df = pd.DataFrame(handler.query(**kwds))
                return df
            elif hasattr(handler, "read"):
                df = pd.DataFrame(handler.read())
                df = df[df["task_name"] == task_name]
                if action is not None:
                    action = [action] if isinstance(action, str) else action 
                    df = df[df["action"].isin(action)]
                if start is not None:
                    df = df[df["asctime"] >= start]
                if end is not None:
                    df = df[df["asctime"] <= end]
                return df
        else:
            raise AttributeError("No handlers that could read the logs (missing methods 'read' or 'query')")

    def get_latest(self):
        df = self.get_records()
        if df.empty:
            return None
        return df.iloc[-1, :]

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