Logging
=======

Red Engine's logging uses ``logging`` from Python standard library.
The main purpose of logging in Red Engine is to maintain the information
which task has run, failed or succeeded and when. This information is needed
to determine the state of many of the conditions. 

Red Engine extends the ``logging`` library to allow also reading the log records.
This is achieved with handlers that write the log records to a more 
structural format such as CSV or JSON. There is also a logging
adapter used as an interface for querying the handlers.

The loggers can be customized in any way using the ``logging`` library itself
or extending it. The most important thing to keep in mind is that the logger
``redengine.task`` should have at least one handler that has method ``.read()``
or ``.query(..)`` to also read the log files. These methods should return
iterble of dictionaries. The method ``.query(...)`` should also be able to handle
the passed queries.

In addition to the regular ``LogRecord`` attributes, the following extras are also set as
extras to the logged records by the tasks or the adapter:

- ``task_name``: Name of the task the log record is about
- ``action``: Action of the task of which the log record is about (success, fail etc.)
- ``start``: Start time of the task as datetime
- ``end``: End time of the task as datetime, not passed if action is ``run``
- ``runtime``: Time it took to run the task as timedelta, not passed if action is ``run``

Both, ``read`` and ``query`` methods, should return an iterable of dictionaries (ie. a list of dict)
and the dictionaries should contain at least the following keys:

- ``task_name``: Name of the task the log record is about
- ``timestamp``, ``created`` or ``asctime``: Time when the log record occurred.
- ``action``: Action of the task of which the log record is about (success, fail etc.)

Querying the task adapter
-------------------------

As stated, ``TaskAdapter`` interfaces the task logging and 
it can be used for querying log records of a specific task.
This can be done with the method ``.get_records(...)`` and 
this method allow several different ways for querying.

.. testsetup:: *

   from redengine.core import Task
   from redengine.log import MemoryHandler, AttributeFormatter
   import logging
   logger = logging.getLogger('redengine.task')
   handler = MemoryHandler()
   handler.records = [
       {"task_name": "mytask", "action": "run", "created": 1638748800}, 
       {"task_name": "mytask", "action": "success", "created": 1638749400},
       {"task_name": "mytask", "action": "run", "created": 1638750000}, 
       {"task_name": "mytask", "action": "fail", "created": 1638750600},
   ]
   logger.handlers = [handler]

>>> from redengine.core import Task
>>> task = Task(name="mytask")
>>> # The TaskAdapter is found as task.logger attribute
>>> task_adapter = task.logger

Querying all:

>>> from pprint import pprint
>>> pprint(list(task_adapter.get_records()))
[{'action': 'run',
  'created': 1638748800,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:00:00')},
 {'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:10:00')},
 {'action': 'run',
  'created': 1638750000,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:20:00')},
 {'action': 'fail',
  'created': 1638750600,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:30:00')}]

Querying a list of actions:

>>> from pprint import pprint
>>> pprint(list(task_adapter.get_records(action=['success', 'fail'])))
[{'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:10:00')},
 {'action': 'fail',
  'created': 1638750600,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:30:00')}]

Querying a specific range:

>>> from pprint import pprint
>>> import datetime
>>> pprint(list(task_adapter.get_records(timestamp=(datetime.datetime(2021, 12, 6, 2, 10), datetime.datetime(2021, 12, 6, 2, 25)))))
[{'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:10:00')},
 {'action': 'run',
  'created': 1638750000,
  'task_name': 'mytask',
  'timestamp': Timestamp('2021-12-06 02:20:00')}]
