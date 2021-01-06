

"""
Utilities for getting information 
about the scehuler/task/parameters etc.
"""

import logging

import pandas as pd

from pypipe.core.log import TaskAdapter
from pypipe.core.task.base import TASKS, Task
from pypipe.core.schedule.schedule import SCHEDULERS
from pypipe.core.parameters import GLOBAL_PARAMETERS

class _Session:
    """Collection of the relevant data and methods
    of the pypipe ecosystem. 

    Returns:
        [type]: [description]
    """
    parameters = GLOBAL_PARAMETERS

    @staticmethod
    def get_tasks():
        return TASKS

    @staticmethod
    def get_schedulers():
        return SCHEDULERS

    @staticmethod
    def get_task_loggers(with_adapters=True) -> dict:
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger 
            for name, logger in logging.root.manager.loggerDict.items() 
            if name.startswith("pypipe.core.task") 
            and not isinstance(logger, logging.PlaceHolder)
        }

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

def _set_run_id(df):
    # Set run_id for run actions
    df_runs = df[df["action"] == "run"]
    df = df.sort_values("asctime")
    df.loc[df_runs.index, "run_id"] = pd.RangeIndex(len(df_runs.index))
    df = df.sort_values("task_name")
    
    # Set run_id for end of runs
    run_ids = {
        task: df[(df["task_name"] == task) & (~df["run_id"].isna())]["run_id"].tolist()
        for task in df["task_name"].unique()
    }
    def find_start(ser):
        task_run_ids = run_ids[ser["task_name"]] 
        return task_run_ids.pop(0)

    df.loc[df.run_id.isna(), "run_id"] = df.loc[df.run_id.isna()].apply(find_start, axis=1)
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