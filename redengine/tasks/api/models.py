
import json

import datetime

from redengine.core.parameters.parameters import Parameters
from redengine.core import Task, BaseCondition
from redengine import Session

class RedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Task):
            return self.encode_task(obj)
        elif isinstance(obj, Session):
            return self.encode_session(obj)
        elif isinstance(obj, Parameters):
            return self.encode_params(obj)
        elif isinstance(obj, (BaseCondition, datetime.datetime, datetime.date, datetime.timedelta)):
            return str(obj)
        else:
            return repr(obj)

    def encode_task(self, obj):
        return obj.to_dict()
    
    def encode_session(self, obj:Session):
        return {
            "config": obj.config,
            "parameters": self.encode_params(obj.parameters),
            "tasks": list(obj.tasks.keys()),
            "returns": self.encode_params(obj.returns),
        }

    def encode_params(self, obj):
        return obj.to_dict()