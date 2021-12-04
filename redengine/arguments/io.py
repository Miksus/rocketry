
from redengine.core.parameters import BaseArgument

class YamlArg(BaseArgument):
    """Argument which value is the return value
    of a function.

    Parameters
    ----------
    path : path-like
        Path to the YAML file
    items : tuple
        Location of the YAML item.
    """
    def __init__(self, path, field=None):
        self.path = path
        self.field = [] if field is None else field

    def get_value(self):
        import yaml
        path = self.path
        with open(path, 'r') as file:
            cont = yaml.safe_load(file)
        
        for field in self.field:
            if isinstance(field, BaseArgument):
                field = field.get_value()
            cont = cont[field]

        return cont