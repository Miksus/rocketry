

class InstanceParser:
    # PROTO
    def __init__(self, classes):
        self.classes = classes

    def parse(self, conf:dict):
        cls_name = conf.pop("class")
        cls = self.classes[cls_name]
        return cls(**conf)


class Field:
    def __init__(self, key, func, types=None, if_missing="ignore"):
        self.key = key
        self.func = func
        self.types = types
        self.if_missing = if_missing
        
    
    def parse(self, d:dict, resources:dict):
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

    def parse(self, d:dict):
        self.validate(d)
        for field in self.fields:
            out = field.parse(d, resources=self.resources)
        return out

    def validate(self, d):
        extra = [key for key in d if key not in self.fields]
        if self.on_extra == "raise":
            raise KeyError(f"Keys {extra} are invalid for the schema")