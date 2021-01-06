
import pytest

from pypipe import Scheduler, JupyterTask
from pypipe.task.base import Task, get_task
from pypipe import reset

from nbconvert.preprocessors import CellExecutionError

Task.use_instance_naming = True


def test_success(tmpdir):
    reset()

    nb_success = r"""{
 "cells": [
  {
   "cell_type": "raw",
   "metadata": {},
   "source": [
    "This is a notebook"
   ]
  },
  {
   "cell_type": "raw",
   "metadata": {
    "tags": [
     "conditions"
    ]
   },
   "source": [
    "from pypipe.conditions import TaskStarted\n",
    "start_condition = TaskStarted(\"mytask\") == 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "x = 5\n",
    "print(x)"
   ]
  }
 ],
 "metadata": {
  "celltoolbar": "Tags",
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
"""
    task_folder = tmpdir.mkdir("tasks")
    task_folder.join("task_success.ipynb").write(nb_success)

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = JupyterTask(
            "tasks/task_success.ipynb", 
            execution="daily",
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir):
    reset()

    nb_failure = r"""{
 "cells": [
  {
   "cell_type": "raw",
   "metadata": {},
   "source": [
    "This is a notebook"
   ]
  },
  {
   "cell_type": "raw",
   "metadata": {
    "tags": [
     "conditions"
    ]
   },
   "source": [
    "from pypipe.conditions import TaskStarted\n",
    "start_condition = TaskStarted(\"mytask\") == 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "x = 5\n",
    "raise RuntimeError('Notebook Failed')"
   ]
  }
 ],
 "metadata": {
  "celltoolbar": "Tags",
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
"""
    task_folder = tmpdir.mkdir("tasks")
    task_folder.join("task_fail.ipynb").write(nb_failure)

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = JupyterTask(
            "tasks/task_fail.ipynb", 
            execution="daily", 
        )
        with pytest.raises(CellExecutionError):
            task()
        assert task.status == "fail"