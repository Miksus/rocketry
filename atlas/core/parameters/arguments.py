

class Argument:
    "Argument is one parameter for a task that may or may not be materialized"
    def __init__(self, value):
        self._value = value
    
    def get_value(self):
        return self._value

    def get_repr(self):
        "Get representation of the value"
        return self._value

    def __eq__(self, other):
        if isinstance(other, Argument):
            return self._value == other._value
        else:
            return self._value == other

class Private(Argument):
    "Argument that is not meant to be shown outside usage"

    def get_repr(self):
        # We override the repr with dummy
        return "*****"

    def get_value(self):
        return self._value