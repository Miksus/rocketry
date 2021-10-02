
.. _simple-session:

Simple Session Configuration
-----------------------------

.. literalinclude:: /../redengine/templates/simple/config.yaml
    :language: yaml

Then read this in a launch file (ie. ``main.py``):

.. code-block:: python

    from redengine import Session
    session = Session.from_yaml("myconf.yaml")
    session.start()
