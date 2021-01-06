import logging

import pandas as pd

from pypipe.log import TaskAdapter

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
            "action_start": "status",
            "action_end": "status",
            "asctime_start": "start",
            "asctime_end": "end",
        }, axis=1
    )
    df["run_time"] = df["end"] - df["start"]
    return df[["run_id", "task_name", "start", "end", "status", "run_time"]]

def get_task_loggers(with_adapter=False):
    return {
        name: TaskAdapter(logger, None) # The adapter should not be used to log (but to read) thus task_name = None
        for name, logger in logging.root.manager.loggerDict.items() 
        if name.startswith("pypipe.task") 
        and not isinstance(logger, logging.PlaceHolder)
    }