.. _hooks:

Extending with hooks
====================

Hooks are simply functions or generators that are 
executed in specific parts of Red Engine's code. 
These are useful for building your logic for 
specific situations where subclassing a base class
would be too complicated.

Hooks are section specific and can run before or after
the section (ie. scheduler start up or task initiation).
If a hook function is a generator (has ``yield``), the
code before the ``yield`` is executed before the section
and code after the ``yield`` is executed after the section.
Multiple yields are not supported.


.. testsetup:: func_hook

   cleanup()

.. testsetup:: gen_hook

   cleanup()

.. autofunction:: redengine.core.Task.hook_init
   :noindex:

.. testcleanup:: func_hook

   cleanup()

.. testcleanup:: gen_hook

   cleanup()

.. autofunction:: redengine.core.Scheduler.hook_startup
   :noindex:

.. autofunction:: redengine.core.Scheduler.hook_cycle
   :noindex:

.. autofunction:: redengine.core.Scheduler.hook_shutdown
   :noindex:
