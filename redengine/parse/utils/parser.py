

from typing import Callable, Dict, Type, Union
import inspect

class DictInstanceParser:
    """[summary]
    Instance represented as:
        {"class": "MyClass"}
    """
    # PROTO
    def __init__(self, classes:Dict[str, Callable], subparsers=None, default:Union[Callable, Type]=None):
        self.classes = classes
        self.subparsers = {} if subparsers is None else subparsers
        self.default = default

    def __call__(self, conf:dict, resources:dict=None, kwds_subparser:dict=None, **kwargs):
        if "class" not in conf and self.default is not None:
            cls = self.default if inspect.isclass(self.default) else self.default(conf, **kwargs)
        else:
            cls_name = conf.pop("class")
            cls = self.classes[cls_name]

        if kwds_subparser is None:
            kwds_subparser = {}

        for key, parser in self.subparsers.items():
            if key in conf:
                conf[key] = parser(conf[key], **kwargs, **kwds_subparser)
        return cls(**conf, **kwargs)


class ParserPicker:
    "Chooses parser depending of conf type"
    def __init__(self, type_parsers, subparsers=None, key_as=None):
        self.type_parsers = type_parsers
        self.subparsers = subparsers
        self.key_as = key_as

    def __call__(self, conf, **kwargs):
        "Parse item"
        parser = self.type_parsers[type(conf)]
        return parser(conf, **kwargs)


class Field:

    def __init__(self, func, types=None, if_missing="ignore", consume=False):
        self.func = func
        self.types = types
        self.if_missing = if_missing
        self.consume = consume
    
    def __call__(self, conf:dict, key, resources:dict, **kwargs):
        if key not in conf:
            if self.if_missing == "raise":
                raise KeyError(f"Config missing key: {self.key}")
            elif self.if_missing == "ignore":
                return 

        if self.consume:
            cont = conf.pop(key)
        else:
            cont = conf[key]
        self.validate(cont, key=key)
        return self.func(cont, resources=resources, **kwargs)

    def validate(self, content, key=None):
        if self.types is not None:
            is_valid_type = isinstance(content, self.types)
            if not is_valid_type:
                raise ValueError(f"Field '{key}' value is invalid type: {type(content)} (expected: {self.types})")


class StaticParser:

    def __init__(self, fields:Dict[str, Field], on_extra="ignore", resources=None):
        self.fields = fields
        self.on_extra = on_extra
        self.resources = resources if resources is not None else {}

    def __call__(self, d:dict, kwds_fields=None, **kwargs):
        self.validate(d)
        kwds_fields = {} if kwds_fields is None else kwds_fields
        for key, field in self.fields.items():
            kwds_field = kwds_fields.get(key, {})
            out = field(d, resources=self.resources, key=key, **kwds_field, **kwargs)
        return out

    def validate(self, d):
        extra = [key for key in d if key not in self.fields]
        if self.on_extra == "raise":
            raise KeyError(f"Keys {extra} are invalid for the schema")

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, item, value):
        # Delete existing key (if there is one with same name)
        field = Field(func=value)
        self.fields[item] = field