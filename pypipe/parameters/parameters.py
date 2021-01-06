

from collections.abc import Mapping
from .arguments import Argument
from pypipe.utils import is_pickleable

class Parameters(Mapping): # Mapping so that mytask(**Parameters(...)) would work

    """

    Example:
        # Creating parameters
        Parameters({
            "mode": "test",
            "rep_date": FuncArg(get_prev_date),
            "conns": YamlArg("databases.yaml")
        })

        # Joining parameters
        Parameters({"mode": "test"}) | Parameters.from_yaml("conf.yaml") | Parameters.from_json("conf.json")
    """

    def __init__(self, **params):
        self._params = params
    
# For mapping interface
    def __iter__(self):
        return iter(self._params)

    def __len__(self):
        return len(self._params)

    def __getitem__(self, item):
        "Materializes the parameters"
        value = self._params[item]
        return value if not isinstance(value, Argument) else value.get_value()

    def __setitem__(self, key, item):
        "Set parameter value"
        self._params[key] = item

    def update(self, params):
        self._params.update(params)

    def __or__(self, other):
        "| operator is union"
        return type(self)(**self._params, **other._params)

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


