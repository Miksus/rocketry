
.. _cond-dependence:

Task Dependence
---------------

**Syntax**

.. code-block:: none

   after task '<task>'
   after task '<task>' [succeeded | failed | finished | terminated]
   after tasks '<task 1>', '<task 2>' ... 
   after tasks '<task 1>', '<task 2>' ... [succeeded | failed | finished]
   after any tasks '<task 1>', '<task 2>' ... [succeeded | failed | finished]

**True when**

  True if the assigned task has not run after the given task has
  succeeded/failed/finished/terminated. Useful for creating 
  task pipelines.

.. note::

  Must be assigned to a task.


**Examples**

.. code-block:: python

    # Creating a dummy task
    FuncTask(..., name="a task")
    
    # Examples
    FuncTask(..., start_cond="after task 'a task'")
    FuncTask(..., start_cond="after task 'a task' succeeded")
    FuncTask(..., start_cond="after task 'a task' failed")
    FuncTask(..., start_cond="after task 'a task' finished")
    FuncTask(..., start_cond="after tasks 'a task', 'another task' finished")