
from pathlib import Path

from redengine.tasks import FuncTask
from redengine.arguments import Return
from redengine import session

ROOT = Path(__file__).parent

@FuncTask(start_cond="daily")
def run_a():
    ... # Do stuff

@FuncTask(start_cond="after task 'run_a'")
def run_b(myarg):
    ... # Do stuff

@FuncTask(start_cond="after task 'run_a' & after task 'run_b'")
def run_c(myarg):
    ... # Do stuff

@FuncTask(start_cond="after task 'run_a' | after task 'run_b'")
def run_d(myarg):
    ... # Do stuff

@FuncTask(start_cond="after task 'run_a' failed | after task 'run_b' failed")
def run_e(myarg):
    ... # Do stuff

import matplotlib.pyplot as plt

fig = plt.figure()
session.dependencies.to_networkx()
fig.savefig(ROOT / 'pipeline.png')