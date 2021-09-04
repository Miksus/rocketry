
from typing import Type

def _add_parser(cls:Type, container:dict) -> None:
    """Acquire the parsers from the class
    and add them to the container.
    """
    def _get_constructor(val, cls):
        if not isinstance(val, str):
            # If not string, e xpecting a function/callable
            return val
        if val == "__init__":
            # cls.__init__ would require the instance, self so we use basic constructor
            return cls
        else:
            # Expecting a class method
            return getattr(cls, val)

    parsers = getattr(cls, "__parsers__", None)
    if not parsers:
        return

    parsers = {
        # Typically a callable is expected but if string given, a method is assumed
        key: _get_constructor(val, cls=cls)
        for key, val in parsers.items()
    }

    container.update(parsers)
    # We delete the attribute to not cause confusion 
    # as changing it does nothing
    delattr(cls, "__parsers__")
