
.. meta::
   :description: Rocketry, modern scheduling framework
   :keywords: schedule, task, script, run, Python

.. raw:: html
   :file: header.html

- `Documentation <https://rocketry.readthedocs.io/>`_
- `Source code (Github) <https://github.com/Miksus/rocketry>`_
- `Releases (PyPI) <https://pypi.org/project/rocketry/>`_

No time to read? :ref:`Get started then. <getting-started>`

Rocketry is a modern scheduling framework for Python 
applications. It is simple, clean and extensive.

**Key features:**

- Simple: Productive and easy to set up
- Robust: Well tested and production ready
- Extensive: A lot of built-in features
- Customizable: Designed to be modified

**Core functionalities:**

- Powerful scheduling
- A lot of built-in scheduling options (including :ref:`cron <handbook-cond-cron>`)
- Concurrency (async, threading, multiprocessing)
- Parametrization
- Task pipelining
- Modifiable runtime session
- Async support

**It looks like this:**

.. literalinclude:: /code/demos/minimal_with_api.py
    :language: py

.. raw:: html

   <details>
   <summary><a>There is also a string based option</a></summary>

.. literalinclude:: /code/demos/minimal.py
    :language: py

.. raw:: html

   </details>

Why Rocketry?
-------------

There are some alternatives for a scheduler:

- Crontab
- APScheduler
- Airflow

Unlike the alternatives, Rocketry's scheduler is 
statement-based. Rocketry natively supports the 
same scheduling strategies as the other options, 
including cron and task pipelining, but it can also be
arbitrarily extended using custom scheduling statements.

In addition, Rocketry is very easy to use. It does not 
require complex setup but it can be used for bigger applications. 
It has a lot of options to fine-tune and a lot of features 
to support various needs.
 
Rocketry is designed to be modified and it suits well as the 
engine for autonomous applications. It is the automation 
back-end that sets your applications alive.

More Examples
-------------

.. raw:: html

   <details>
   <summary><a>Choosing Execution Option</a></summary>

.. literalinclude:: /code/snippets/parallelization.py
    :language: py

.. raw:: html

   </details>


.. raw:: html

   <details>
   <summary><a>Custom Conditions</a></summary>

.. literalinclude:: /code/snippets/custom_condition.py
    :language: py

.. raw:: html

   </details>


.. raw:: html

   <details>
   <summary><a>Pipelining Tasks</a></summary>

.. literalinclude:: /code/snippets/pipeline.py
    :language: py

.. raw:: html

   </details>


.. raw:: html

   <details>
   <summary><a>Parametrizing Tasks</a></summary>

.. literalinclude:: /code/snippets/parametrize.py
    :language: py

.. raw:: html

   </details>


Interested?
-----------

Just install the library:

.. code-block:: console

    pip install rocketry

There is much more to offer. See :ref:`quick start <getting-started>`
and get started with :ref:`tutorials <tutorials>`. There are also 
:ref:`handbooks <handbooks>` to check options and details.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   handbooks/index
   cookbook/index
   examples/index
   condition_syntax/index
   how_it_works
   rocketry_vs_alternatives
   contributing
   versions


Indices and tables
==================

* :ref:`genindex`
