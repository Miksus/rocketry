from collections.abc import Mapping
from typing import Callable, Type, Union, TYPE_CHECKING
from functools import partial
import inspect

from rocketry._base import RedBase
from rocketry.core.utils import is_pickleable
from rocketry.core.utils import filter_keyword_args

from .arguments import BaseArgument

if TYPE_CHECKING:
    import rocketry

class Parameters(RedBase, Mapping): # Mapping so that mytask(**Parameters(...)) would work
    """Parameter set for tasks.

    Parameter set is a mapping (like dictionary).
    The parameter set materializes the arguments so that
    those can be passed to the tasks.

    Parameters
    ----------
    _param : dict, Parameters, optional
        Arguments.
    type_ : Type, optional
        Type of Argument the keyword arguments are
        turned into.
    **params : dict
        Arguments.
    """

    _params: dict
    session: 'rocketry.Session'

    def __init__(self, _param:Union[dict, 'Parameters']=None, type_:Type[BaseArgument]=None, **params):
        if _param is not None:
            # We get original values if _param has Private or other arguments that are
            # hidden
            _param = _param._params if isinstance(_param, Parameters) else _param
            params.update(_param)

        if type_ is not None:
            params = {
                name: type_(value)
                for name, value in params.items()
            }
        self._params = params

    @classmethod
    def _from_signature(cls, __func:Callable, **kwargs) -> 'Parameters':
        # Get parameters from a function signature
        # ie.
        # def myfunc(task=Task(), session=Session()): ...
        func_params = inspect.signature(__func).parameters
        params = cls()
        for name, param in func_params.items():
            default = param.default
            if isinstance(default, BaseArgument):
                params[name] = default
        return params

# For mapping interface
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _get(self, __item, **kwargs):
        item = __item
        if callable(item) and hasattr(item, "__rocketry__") and "param_name" in item.__rocketry__:
            item = item.__rocketry__['param_name']
        value = self._params[item]
        return value if not isinstance(value, BaseArgument) else value.get_value(**kwargs)

    def __iter__(self):
        return iter(self._params)

    def __len__(self):
        return len(self._params)

    def __getitem__(self, item):
        "Materializes the parameters and hide private"
        return self._get(item)

    def pre_materialize(self, *args, **kwargs):
        """Turn arguments to their values before passed
        to child processes/threads.
        """
        self._params = {
            key:
                value
                if not isinstance(value, BaseArgument)
                else value.stage(*args, **kwargs)
            for key, value in self._params.items()
        }
        return self

    def materialize(self, *args, **kwargs):
        """Turn arguments to their values (after passed
        to child processes/threads). These should be their
        final values.
        """

        return {
            key:
                value
                if not isinstance(value, BaseArgument)
                else value.get_value(*args, **get_kwargs(value.get_value, **kwargs))
            for key, value in self._params.items()
        }

    def __setitem__(self, key, item):
        "Set parameter value"
        self._params[key] = item

    def update(self, params):
        params = params._params if isinstance(params, Parameters) else params
        self._params.update(params)

    def param_func(self, _func:Callable=None, *, key:str=None):
        """Add a function as an argument to the parameters.

        Parameters
        ----------
        _func : Callable
            Function to form the argument from.
        key : str, optional
            Key or the name of the argument,
            by default the name of the function
        """
        from rocketry.args import FuncArg
        if _func is None:
            return partial(self.param_func, key=key)

        if key is None:
            key = _func.__name__

        kwargs = filter_keyword_args(_func, session=self.session)
        arg = FuncArg(_func, **kwargs)
        self[key] = arg

        # NOTE, we return the func for not to anger the picking
        # gods. We are in deep shit with subprocesses otherwise.
        # See: https://bugs.python.org/issue1121475
        return _func

    def __repr__(self):
        cls_name = type(self).__name__
        params = ', '.join(f'{name}={repr(arg)}' for name, arg in self._params.items())
        return f'{cls_name}({params})'

    def __or__(self, other):
        "| operator is union"
        left = self._params
        right = other._params if isinstance(other, Parameters) else other

        params = {**left, **right}
        return type(self)(**params)

    def __eq__(self, other):
        "Whether parameters are equal"
        if isinstance(other, Parameters):
            return self._params == other._params
        return False

    def __ne__(self, other):
        "Whether parameters are equal"
        if isinstance(other, Parameters):
            return self._params != other._params
        return True

# Pickling
    def __getstate__(self):
        # capture what is normally pickled
        state = self.__dict__.copy()

        # Remove unpicklable parameters
        state["_params"] = {
            key: val
            for key, val in state["_params"].items()
            if is_pickleable(val)
        }
        return state

#    def __setstate__(self, newstate):
#        self.__dict__.update(newstate)

    def items(self):
        return self._params.items()

    def keys(self):
        return self._params.keys()

    def clear(self):
        "Empty the parameters"
        self._params = {}

    def copy(self):
        return Parameters(self._params.copy())

    def to_dict(self):
        return self._params

    def to_json(self):
        "Put parameters to dict that is JSON serializable"
        return {
            key: val if hasattr(val, "to_json") else repr(val)
            for key, val in self._params.items()
        }

def get_kwargs(__func, **kwargs) -> dict:
    "Get function arguments"
    sig_kwargs = Parameters._from_signature(__func).materialize(**kwargs)
    return {**sig_kwargs, **kwargs}