
from datetime import date, datetime

from flask.json import JSONEncoder

from redengine.core import Task, Parameters
from redengine.pybox.meta.check.strong_type import is_function, is_builtin, is_class
from redengine.core import Task, Parameters

class RedengineJSONEncoder(JSONEncoder):

    cls_properties = {
        "FuncTask": ["func"]
    }

    def default(self, obj):
        if isinstance(obj, Task):
            return self.format_task(obj)
        elif isinstance(obj, Parameters):
            return self.format_params(obj)
        elif isinstance(obj, (date, datetime)):
            # Turn to iso format
            return obj.isoformat(sep=" ")

        try:
            return super().default(obj)
        except TypeError:
            try:
                if is_builtin(obj):
                    return obj.__name__
                elif is_function(obj) or is_class(obj):
                    module = obj.__module__
                    if module == "__main__":
                        return obj.__qualname__
                    else:
                        return module + "." + obj.__qualname__
                else:
                    return str(obj)
            except AttributeError:
                return str(obj)

    def format_task(self, task):
        attrs = {
            key: val
            # Turns instance's attributes to dict
            for key, val in vars(task).items()
            if not key.startswith("_") # No private attrs
            and key not in ("thread_terminate",)
        }
        props = {
            "name": task.name,
            "class": type(task),
            # Some properties won't otherwise end up here
            "name": task.name,
            "execution": task.execution,
            "start_cond": task.start_cond,
            "end_cond": task.end_cond,
            "status": task.status,
            "logger": task.logger.name,
            "parameters": dict(**task.parameters),
        }
        extra = {
            prop: getattr(task, prop)
            for prop in self.cls_properties.get(type(task).__name__, [])
        }
        return {**attrs, **props, **extra}

    def format_params(self, params):
        return params.materialize()

