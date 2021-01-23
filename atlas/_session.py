

"""
Utilities for getting information 
about the scehuler/task/parameters etc.
"""

import logging
from pathlib import Path
import pandas as pd

from atlas.core.log import TaskAdapter
from atlas.core.task.base import Task, clear_tasks, get_task, get_all_tasks
from atlas.core.schedule.schedule import Scheduler, clear_schedulers, get_all_schedulers


from atlas.core.parameters import Parameters, GLOBAL_PARAMETERS
from atlas.log import CsvHandler, CsvFormatter

class _Session:
    """Collection of the relevant data and methods
    of the atlas ecosystem. 

    Returns:
        [type]: [description]
    """
    # TODO:
    #   .reset() Put logger to default, clear Parameters, Schedulers and Tasks
    #   .
    
    # Global parameters
    _global_parameters = GLOBAL_PARAMETERS

    @staticmethod
    def get_tasks():
        return get_all_tasks()

    @staticmethod
    def get_task(task):
        return get_task(task)

    @staticmethod
    def get_schedulers():
        return get_all_schedulers()

    @staticmethod
    def get_task_loggers(with_adapters=True) -> dict:
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger 
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith(Task._logger_basename) 
            and not isinstance(logger, logging.PlaceHolder)
        }

# Log data
    def get_task_log(self, **kwargs):
        loggers = self.get_task_loggers(with_adapters=True)
        dfs = [
            logger.get_records(**kwargs)
            for logger in loggers.values()
        ]
        return pd.concat(dfs, axis=0)

    def get_task_run_info(self, **kwargs):
        df = self.get_task_log(**kwargs)
        return get_run_info(df)

    def get_task_info(self):
        return pd.DataFrame([
            {
                "name": name, 
                "priority": task.priority, 
                "timeout": task.timeout, 
                "start_condition": task.start_cond, 
                "end_condition": task.end_cond
            } for name, task in session.get_tasks().items()
        ])

    def reset(self):
        "Set Pypipe ecosystem to default settings (clearing tasks etc)"
        clear_tasks()
        clear_schedulers()

        self.parameters.clear()

        # Setting task logger
        log_file = "log/task.csv"
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        task_logger = logging.getLogger(Task._logger_basename)
        task_logger.handlers = []

        handler = CsvHandler(log_file, delay=True)
        handler.setFormatter(
            CsvFormatter(
                fields=[
                    "asctime",
                    "levelname",
                    "action",
                    "task_name",
                    "exc_text",
                ]
            )
        )

        task_logger.addHandler(handler)
        task_logger.setLevel(logging.INFO)

        # Set scheduler logger
        sched_logger = logging.getLogger(Scheduler._logger_basename)
        Scheduler.logger = sched_logger
        
    @property
    def parameters(self):
        "Readonly attribute"
        return self._global_parameters


def _set_run_id(df):
    # Set run_id for run actions
    if df.empty:
        df["run_id"] = None
        return df
    
    df = df.sort_values(["asctime"]) # , ascending=False
    
    mask = df["action"] == "run"
    n_runs = mask.sum()
    df.loc[mask, "run_id"] = pd.RangeIndex(n_runs)

    df_runs = df[df["action"] == "run"].set_index("run_id")
    
    def find_start(ser):
        # Take all run ids of the task before success/failure time
        task_run_ids = df_runs[
            (df_runs["task_name"] == ser["task_name"])
            & (df_runs["asctime"] <= ser["asctime"])
        ]
        if task_run_ids.empty:
            return None

        # FIFO: take earliest unconsumed run id
        run_id = task_run_ids.index.min()
        
        # Consume the task_run_id
        df_runs.drop(run_id, inplace=True, axis=0)
        
        return run_id
    
    df = df.sort_values("asctime")
    task_ends = df.run_id.isna()
    df.loc[task_ends, "run_id"] = df.loc[task_ends].apply(find_start, axis=1)
    return df

def get_run_info(df):
    "Task logging dataframe to run info dataframe"
    df["asctime"] = pd.to_datetime(df["asctime"])
    
    df = _set_run_id(df)

    # Join start of runs to finish of runs (works even if missing start or end)
    df = pd.merge(
        df[df["action"] == "run"],
        df[df["action"] != "run"],
        how="left",
        left_on="run_id", right_on="run_id",
        suffixes=("_start", "_end"),
    )
    # Rename and format
    df = df.rename(
        {
            "task_name_start": "task_name",
            "action_end": "status",
            "asctime_start": "start",
            "asctime_end": "end",
        }, axis=1
    )
    df["run_time"] = df["end"] - df["start"]
    return df[["run_id", "task_name", "start", "end", "status", "run_time"]]


session = _Session()