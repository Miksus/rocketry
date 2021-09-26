from redengine.core.parameters import Argument

class FuncArg(Argument):
    "Argument of which value is determined by a function"
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def get_value(self):
        return self.func(**self.kwargs)