
from atlas.core.task import base
from atlas.core.conditions import Statement

import psutil
import os
import datetime
import numpy as np

import logging
logger = logging.getLogger(__name__)


# OS related
@Statement.from_func(historical=False, quantitative=True)
def RamFree(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return 1 - memory.percent / 100
    else:
        return memory.available

@Statement.from_func(historical=False, quantitative=True)
def RamUsed(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return memory.percent / 100
    else:
        return memory.used

@Statement.from_func(historical=False, quantitative=False)
def FileExists(filename):
    return os.path.exists(filename)

# GIT
@Statement.from_func(historical=True, quantitative=False)
def LastCommitted(_start_, _end_, repo=None):
    repo = Repo(repo)
    last_commit = next(iter(repo.iter_commits()))
    dt = pd.Timestamp(last_commit.committed_date, unit="s")
    return _start_ <= dt <= _end_