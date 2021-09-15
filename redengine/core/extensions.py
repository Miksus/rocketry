
from redengine.parse import parse_session
from redengine.parse.utils import instances, ParserPicker
from redengine.core.meta import _register

CLS_EXTENSIONS = {}
PARSERS = {}

def _get_parser(init_method):
    return ParserPicker(
        {
            dict: instances.DictParser(instance_parser=init_method, key_as_arg="name"),
            list: instances.ListParser(instance_parser=init_method)
        }
    )

class _ExtensionMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)

        # Store the name and class for configurations
        parse_key = getattr(cls, "__parsekey__", None)
        if parse_key is not None:
            parser = _get_parser(cls.parse_cls)
            parse_session[parse_key] = parser
            PARSERS[parse_key] = parser
        _register(cls, CLS_EXTENSIONS)
        return cls

class BaseExtension(metaclass=_ExtensionMeta):
    """Base for all extensions that are registered
    to the sessions and are parsable in configs.

    Extension is an external class that extends the
    existing behaviour of Redengine but does not 
    much interfer with it by default. 

    Examples of extensions could be:
        - Task sequences or pipelines so 
          that tasks are run after each 
          other.
        - Task groups so the attributes of 
          multiple tasks can be changed at
          once.
        - Parameter groups so they can be
          changed at once.
    """
    session: 'Session'
    __parsekey__: str
    __register__ = False

    def __init__(self, name:str=None, session:'Session'=None):
        "Add the extension to the session"
        parse_key = self.__parsekey__
        if parse_key not in self.session.extensions:
            self.session.extensions[parse_key] = {}
        self.session.extensions[parse_key][name] = self

        self.session = session if session is not None else self.session
        self.name = name

    @classmethod
    def parse_cls(cls, d:dict, session:'Session'):
        return cls(**d, session=session)

    def delete(self):
        "Remove the extension from the session"
        del self.session.extensions[self.__parsekey__][self.name]
