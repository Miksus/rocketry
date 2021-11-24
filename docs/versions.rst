
Version history
===============

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