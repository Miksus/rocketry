
from typing import Callable

class ListParser:
    """
    Parse list of instances. Each item in the list 
    represent an instance that is parsed using 
    specified function/method/object with __call__.
    """
    def __init__(self, instance_parser:Callable):
        self.instance_parser = instance_parser

    def __call__(self, conf, **kwargs):
        return [self.instance_parser(instance_conf, **kwargs) for instance_conf in conf]

class DictParser:
    """
    Parse dict of dict of instances. Key of the parent 
    dict is set as the value of the 'key_as_arg' in
    the subdict. Typically 'key_as_arg' is a name/id
    that is used in the __init__ of the instance.
    """
    def __init__(self, instance_parser:Callable, key_as_arg):
        self.instance_parser = instance_parser
        self.key_as_arg = key_as_arg

    def __call__(self, conf, **kwargs) -> list:
        instances = []
        for name, conf in conf.items():
            conf[self.key_as_arg] = name
            instance = self.instance_parser(conf, **kwargs)
            instances.append(instance)
        return instances

