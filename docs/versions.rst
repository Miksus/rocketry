
Version history
===============

- ``2.5.0``

    - Add: Multi-launch system. Same task can now be run several times parallel.

        Run stacks were implemented to track the execution of each run. These
        runs can be tracked in the logs using the field ``run_id``.

    - Update: ``rocketry.conds.running`` refactored to support multi-launch.

- ``2.4.1``

    - Fix: Warnings about ``task_execution`` in import
    - Docs: Fixed typos
    - Clean: Cleaned code base according to Pylint

- ``2.4.0``

    - Add: New condition, ``Retry``
    - Add: New condition to condition API, ``crontime``
    - Add: New condition to condition API, ``scheduler_cycles`` (useful for testing)
    - Add: New arguments, ``EnvArg`` and ``CliArg``
    - Add: Argument pipelining, ``Arg('missing') >> Arg('found')``
    - Add: Now tasks can be set running with parameters using ``task.run(arg="value")``
    - Add: Config option ``silence_task_logging`` to silence logging errors
    - Fix: Async and threaded tasks no longer limit max simultaneous processes
    - Fix: Timeperiod ``at`` for end of a period, ie. ``daily.at("23:00")``
    - Fix: More consistent parameters
    - Update: Async will be default execution in the future. Warns if execution not defined

- ``2.3.0``

    - Add: Cron style scheduling
    - Add: Task groups (``Grouper``) to support bigger applications
    - Add: New condition, ``TaskRunnable``
    - Add: New methods to session (``remove_task`` & ``create_task``)
    - Add: ``always`` time period
    - Fix: Various bugs related to ``Any``, ``All`` and ``StaticInterval`` time periods
    - Fix: Integers as start and end in time periods
    - Update: Now time periods are immutable 
    - Update: Now if session is not specified, tasks create new one.

- ``2.2.0``

    - Add: Async support
    - Add: More conditions in condition API
    - Add: Support for nested parameters
    - Update: ``session.shutdown`` renamed to ``session.shut_down``
    - Fix: Task crash (scheduler suddenly exists) are now properly logged
    - Fix: ``TaskStarted`` condition's bug in optimization.
    - Fix: Task to JSON
    - Docs: Improved handbook.

- ``2.1.2``

    - Fix: Bug in task persistence. Task last action times were not queried.
    - Docs: Added logging handbook.

- ``2.1.1``

    - Fix: bug in func condition parametrizing

- ``2.1.0``

    - Add: Condition API (``rocketry.conds``) for easy alternative for the string syntax
    - Add: Now ``rocketry.args.Return`` accepts passing the task function
    - Add: Now ``app.cond(..)`` decorator returns the condition (instead of the function)
    - Add: Now conditions accept verbose arguments similarly as tasks do
    - Fix: typing import error for Python 3.7
    - Update: Now conditions are less stateful and they require passing the context when the status is inspected
    - Refactor: The condition mechanism under the hood
    - Requirements: Removed Pandas from dependencies
    - Deprecated: ``session.task_exists``

- ``2.0.1``

    - Fix: ``Rocketry(logger_repo=...)`` now does not remove previous handlers
    - Deprecate: Deprecated ``Rocketry(...).set_logger`` method
    - Docs: Fixed typos in documentation and added docstrings

- ``2.0.0``

    - Update: Completely refactored the interface
    - Remove: Removed a lot of old, poorly supported code

- ``1.2.0``

    - Add: shortcut condition syntax for multiple dependencies
    - Add: new task ``FlaskAPI`` and ``JSONAPI``
    - Add: task dependency view
    - Add: new task ``CodeTask``
    - Add: new hook ``Task.hook_execute``
    - Fix: Bug in ``Return`` if a task executes too quickly
    - Fix: Major bug in optimized task conditions
    - Deprecate: Extensions should no longer be used
    - Update: Now hooks, parsers and task classes are stored in sessions
    - Update: A lot of undocumented code under the hood was removed
    - Update: Removed unsupported templates

- ``1.1.0``

    - Add: conditions ``FuncCond`` and ``TaskCond``
    - Add: new statements to condition syntax
    - Add: new argument ``Return`` and parameter pipelining
    - Add: ``FuncParam``, similar to ``FuncTask`` and ``FuncCond``
    - Fix: Minor bugs
    - Requirements: dropped Pyyaml in hard dependencies
    - Optimization: Now conditions read logs only if cannot be determined without. Can be switched off.

- ``1.0.0``

    - First stable release