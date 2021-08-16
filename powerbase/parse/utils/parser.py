

class DictInstanceParser:
    """[summary]
    Instance represented as:
        {"class": "MyClass"}
    """
    # PROTO
    def __init__(self, classes:dict, subparsers=None, default=None):
        self.classes = classes
        self.subparsers = {} if subparsers is None else subparsers
        self.default = default

    def __call__(self, conf:dict, **kwargs):
        if "class" not in conf and self.default is not None:
            cls = self.default
        else:
            cls_name = conf.pop("class")
            cls = self.classes[cls_name]

        for key, parser in self.subparsers.items():
            if key in conf:
                conf[key] = parser(conf[key], **kwargs)
        return cls(**conf)


class ParserPicker:
    "Chooses parser depending of conf type"
    def __init__(self, type_parsers, subparsers=None, key_as=None):
        self.type_parsers = type_parsers
        self.subparsers = subparsers
        self.key_as = key_as

    def __call__(self, conf, **kwargs):
        parser = self.type_parsers[type(conf)]

        return parser(conf, **kwargs)

class Field:
    def __init__(self, key, func, types=None, if_missing="ignore"):
        self.key = key
        self.func = func
        self.types = types
        self.if_missing = if_missing
    
    def __call__(self, d:dict, resources:dict):
        if self.key not in d:
            if self.if_missing == "raise":
                raise KeyError(f"Config missing key: {self.key}")
            elif self.if_missing == "ignore":
                return 

        cont = d[self.key]
        self.validate(cont)
        return self.func(cont, resources=resources)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.key == other
        else:
            return self.key == other.key

    def validate(self, content):
        if self.types is not None:
            is_valid_type = isinstance(content, self.types)
            if not is_valid_type:
                raise ValueError(f"Field's '{self.key}' value is invalid type {type(content)}")


class StaticParser:
    def __init__(self, *fields, on_extra="ignore", resources=None):
        self.fields = fields
        self.on_extra = on_extra
        self.resources = resources if resources is not None else {}

    def __call__(self, d:dict):
        self.validate(d)
        for field in self.fields:
            out = field(d, resources=self.resources)
        return out

    def validate(self, d):
        extra = [key for key in d if key not in self.fields]
        if self.on_extra == "raise":
            raise KeyError(f"Keys {extra} are invalid for the schema")