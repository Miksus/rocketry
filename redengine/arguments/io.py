
import yaml
from redengine.core.parameters import Argument

class FuncArg(Argument):
    "Argument of which value is determined by a function"
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def get_value(self):
        return self.func(**self.kwargs)

class YamlArg(Argument):

    def __init__(self, path, items=None):
        self.path = path
        self.items = [] if items is None else items

    def get_value(self):
        path = self.path
        with open(path, 'r') as file:
            cont = yaml.safe_load(file)
        
        for item in self.items:
            if isinstance(item, Argument):
                item = item.materialize()
            cont = cont[item]

        return cont