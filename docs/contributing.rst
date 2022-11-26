
Contributing
============

All help is welcome. There are several ways to contribute:

- `Sponsoring <https://github.com/sponsors/Miksus>`_
- `Report an issue (bug, feature request etc.) <https://github.com/Miksus/rocketry/issues>`_
- `Do code a change <https://github.com/Miksus/rocketry/pulls>`_
- `Join the discussion <https://github.com/Miksus/rocketry/discussions>`_

Sponsoring
----------

If you represent a company and your project has benefited from Rocketry, consider sponsoring the free
open-source project to ensure further development and maintenance:

.. raw:: html

    <iframe src="https://github.com/sponsors/Miksus/button" title="Sponsor Miksus" height="35" width="116" style="border: 0;"></iframe>

The project is developed with passion but creating high-quality code is hard and time consuming.
All support is welcome.

Have an Idea?
-------------

If you have a concrete idea of a feature you wish Rocketry had, 
feel free to open `a feature request <https://github.com/Miksus/rocketry/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=ENH>`_.

If you have ideas about broader or more abstract features or would like to discuss about the future directions of the framework, 
feel free to open a discussion about it to `Rocketry's discussion board <https://github.com/Miksus/rocketry/discussions>`_.

Found a bug?
------------

If you found a bug,
`please report it as a bug <https://github.com/Miksus/rocketry/issues/new?assignees=&labels=bug&template=bug_report.md&title=BUG>`_.

Unclear documentation?
----------------------

If you found an issue with the documentation,
`please report it <https://github.com/Miksus/rocketry/issues/new?assignees=&labels=documentation&template=documentation_improvement.md&title=DOCS>`_.

Want to do a code contribution?
------------------------------- 

Good place to start is to look for open issues 
`from issue tracker <https://github.com/Miksus/rocketry/issues>`_. 

If you found a problem and the fix is simple, you don't have to create an issue 
for it. Complex changes require an issue.

Development Guidelines
^^^^^^^^^^^^^^^^^^^^^^

How to do code contribution:

1. Create an issue (you don't need an issue if it's simple)
2. Fork and clone the project
3. Do your changes
4. Run the tests locally or check the documentation
5. Create a pull request

There are some criteria that new code must pass:

- Well tested (with unit tests)
- Well documented
- No breaking changes (unless strictly necessary)
- Follows best practices and standard naming conventions

Improving documentation
^^^^^^^^^^^^^^^^^^^^^^^

If you made a change to documentation, please build them by:
```
pip install tox
tox -e docs
```
Then go to the ``/docs/_build/html/index.html`` and check the 
change looks visually good.

Improving code
^^^^^^^^^^^^^^

To do code changes:

1. Open an issue (unless trivial)
2. Fork and clone the repository
3. Do the changes
4. Run the tests (see below)
5. Do a pull request

To run the tests, you can use tox:

```
pip install tox
tox
```

To ensure your pull request gets approved:

- Create unit tests that demonstrates the bug it fixed or the feature implemented
- Write documentation (unless it's a bug fix)
- Ensure standard behaviour raises no warnings
- Ensure the code follows best practices and fits to the project

Don't feel overwhelmed with these, there are automatic pipelines to ensure code quality
and your code can be updated after the pull request. Rocketry's maintainers understand 
that you are using your free time to contribute on free open-source software.
