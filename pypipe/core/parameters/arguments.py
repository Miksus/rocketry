

class Argument:
    "Argument is one parameter for a task that may or may not be materialized"
    def __init__(self, value):
        self._value = value
    
    def get_value(self):
        return self._value

