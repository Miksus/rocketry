import pytest

from pypipe import Scheduler, JupyterTask
from pypipe.task.base import Task
from pypipe import reset

def test_from_folder(tmpdir):
    # Going to tempdir to dump the log files there
    reset()

    nb_a = """
{
 "cells": [
  {
   "cell_type": "raw",
   "metadata": {
    "tags": [
     "conditions"
    ]
   },
   "source": [
    "start_condition = dummy == 0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "x = 5"
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

    nb_b = """
{
 "cells": [
  {
   "cell_type": "raw",
   "metadata": {
    "tags": [
     "conditions"
    ]
   },
   "source": [
    "start_condition = dummy == 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "x = 5"
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
    with tmpdir.as_cwd() as old_dir:
        task_folder = tmpdir.mkdir("tasks")
        task_folder.join("task_a.ipynb").write(nb_a)
        task_folder.join("task_b.ipynb").write(nb_b)
        tasks = JupyterTask.from_folder("tasks/")
        assert tasks[0].name == "task_a"
        assert tasks[1].name == "task_b"

        assert tasks[0].start_cond.kwargs["__eq__"] ==  0
        assert tasks[1].start_cond.kwargs["__eq__"] ==  1