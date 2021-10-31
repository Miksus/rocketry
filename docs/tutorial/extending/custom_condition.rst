.. _cust-cond:

Custom Condition
================

Custom conditions can be made by subclassing 
:class:`redengine.core.BaseCondition`.

Here is a practical demonstration:

.. code-block:: python

    import re
    from pathlib import Path
    from redengime.core import BaseCondition

    class FileExists(BaseCondition):

        __parsers__ = {
            # These are regex and the functions or names of the methods
            # we add to the parsing engine.
            re.compile(r"file '(?P<file>.+)' exists"): "__init__"
        }

        def __init__(self, file):
            self.file = file

        def __bool__(self):
            # This must return True or False
            return Path(self.file).is_file()

Note that we added a custom parsing logic (``__parsers__``) so that we
can directly use it in the ``start_cond`` of a task, like:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="file 'mydata.csv' exists")
    def mytask():
        ...

This task will start when file `mydata.csv` exists.