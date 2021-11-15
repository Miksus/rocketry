Extending with subclassing
==========================

Red Engine can be extended by creating custom 
classes by subclassing the bases. 

There are several base classes to subclass:

- :class:`redengine.core.Task`: For custom tasks.
- :class:`redengine.core.BaseCondition`: For custom conditions.
- :class:`redengine.core.BaseExtension`: For custom extensions.
- :class:`redengine.core.BaseArgument`: For custom arguments that are passed to functions as parameters.



Base classes
------------

This section contains the details of the base classes and the main 
methods and attributes to override. It is pretty exhaustive.

.. autoclass:: redengine.core.Task
   :members: execute, prefilter_params, postfilter_params, get_default_name
   :noindex:

.. autoclass:: redengine.core.BaseCondition
   :special-members:
   :members: __bool__
   :noindex:
   

.. autoclass:: redengine.core.BaseExtension
   :members: at_parse, delete
   :noindex:


.. autoclass:: redengine.core.BaseArgument
   :members:
   :noindex: