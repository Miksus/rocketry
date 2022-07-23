.. _condition-syntax:

Condition Syntax
================

Condition syntax is the highest level in terms of creating 
conditions. It is a string syntax which is parsed by Rocketry's
condition parser. It is fast to type and simple. It is very 
suitable for quick scheduling or in simple applications
but the downside is that static code analyzers 
cannot inspect the correctness of these statements.


.. note::

    This section does not go into details (please see them from
    :ref:`condition API handbook <condition-api>`) but rather
    show the same examples with the condition syntax.

Here are some examples:

.. literalinclude:: /code/conds/syntax/simple.py
    :language: py

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   logical
   periodical
   pipeline
