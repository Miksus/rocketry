from typing import Any, TYPE_CHECKING
from abc import abstractmethod

from rocketry._base import RedBase

if TYPE_CHECKING:
    import rocketry

class BaseArgument(RedBase):
    """Base class for Arguments.

    Argument is a wrapper for value that can be
    passed to a task. The value can be formulated
    on the fly or it can be a constant variable.

    Examples
    --------

    Minimum example:

    >>> from rocketry.core import BaseArgument
    >>> class MyArgument(BaseArgument):
    ...     def __init__(self, value):
    ...         self.value = value
    ...
    ...     def get_value(self):
    ...         value = self.value
    ...         ... # Code that forms the argument value
    ...         return value
    ...
    >>> from rocketry.core import Parameters
    >>> Parameters(myarg=MyArgument("value"))
    Parameters(myarg=MyArgument('value'))

    """
    session: 'rocketry.Session'

    @abstractmethod
    def get_value(self, **kwargs) -> Any:
        """Get the actual value of the argument.
        Override for custom behaviour.

        Parameters
        ----------
        task : rocketry.core.Task, optional
            Task that requested the value of the argument.
        """

    def stage(self, **kwargs) -> 'BaseArgument':
        """Get (a copy of) the argument with a
        value that can be passed to child threads
        or processes. Override for custom behaviour.

        Example use cases:

            - Save a complex object to disk and read
              it again later with ``get_value``.
            - Shut a file buffer and reopen it when
              in the child process/thread.
            - Remove non-picklable attributes.

        Parameters
        ----------
        task : rocketry.core.Task, optional
            Task that requested the value of the argument.

        Notes
        -----
        It is advisable to copy the argument in order
        not to interfere with the passing of the argument
        in later situations.

        Returns
        -------
        BaseArgument
            Argument that is ready to be passed to a child
            thread or process.
        """
        return self.get_value(**kwargs)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.get_value() == other.get_value()
        return False

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}({repr(self.get_value())})'

    def __str__(self):
        return str(self.get_value())

    def __rshift__(self, other):
        args = []
        if not isinstance(other, BaseArgument):
            raise TypeError(f"Invalid type {type(other)}")
        for inst in (self, other):
            if isinstance(inst, PipeArg):
                args += list(inst)
            else:
                args.append(inst)
        return PipeArg(args)

class PipeArg(BaseArgument):

    def __init__(self, args:list):
        self._args = args

    def __iter__(self):
        return iter(self._args)

    def get_value(self, **kwargs) -> Any:
        for arg in self:
            try:
                return arg.get_value(**kwargs)
            except KeyError:
                continue
        raise KeyError("No value found")
