import datetime
from typing import Optional
from pydantic import field_validator, BaseModel, Field

from rocketry.pybox.time import to_datetime, to_timedelta

class MinimalRecord(BaseModel):
    """A log record with minimal number of fields for Rocketry to work"""
    task_name: str
    action: str = Field(description="Scheduler action: 'run', 'success', 'fail'")
    created: float

class LogRecord(MinimalRecord):
    """A logging record

    See attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
    """
    name: str
    msg: str
    levelname: str
    levelno: int
    pathname: str
    filename: str
    module: str
    exc_text: Optional[str] = Field(description="Exception text")
    lineno: int
    funcName: str
    created: float
    msecs: float
    relativeCreated: float
    thread: int
    threadName: str
    processName: str
    process: int
    message: str

    formatted_message: str = Field(description="Formatted message. This field is created by RepoHandler.")

class TaskLogRecord(MinimalRecord):

    start: Optional[datetime.datetime] = None
    end: Optional[datetime.datetime] = None
    runtime: Optional[datetime.timedelta] = None

    message: str
    exc_text: Optional[str] = None

    @field_validator("start", mode="before")
    @classmethod
    def format_start(cls, value):
        if value is not None:
            value = to_datetime(value)
        return value

    @field_validator("end", mode="before")
    @classmethod
    def format_end(cls, value):
        if value is not None:
            value = to_datetime(value)
        return value

    @field_validator("runtime", mode="before")
    @classmethod
    def format_runtime(cls, value):
        if value is not None:
            value = to_timedelta(value)
        return value

class MinimalRunRecord(MinimalRecord):
    run_id: Optional[str] = None

class RunRecord(LogRecord):
    run_id: Optional[str] = None

class TaskRunRecord(TaskLogRecord):
    run_id: Optional[str] = None
