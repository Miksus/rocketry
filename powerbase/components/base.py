
from powerbase.parse import parse_session
from powerbase.parse.utils import instances, ParserPicker

def _get_parser(init_method):
    return ParserPicker(
        {
            dict: instances.DictParser(instance_parser=init_method, key_as_arg="name"),
            list: instances.ListParser(instance_parser=init_method)
        }
    )

class _ComponentMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)

        # Store the name and class for configurations
        parse_key = getattr(cls, "__parsekey__", None)
        if parse_key is not None:
            parse_session[parse_key] = _get_parser(cls.parse_cls)

        return cls

class BaseComponent(metaclass=_ComponentMeta):
    """Base for all components that are registered
    to the sessions and are parsable in configs.

    Component is an external class that extends the
    existing behaviour of Powerbase but does not 
    much interfer with it by default. 

    Examples of components could be:
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

    def __init__(self, name:str=None, session:'Session'=None):
        "Add the component to the session"
        cls = type(self)
        if cls not in self.session.components:
            self.session.components[cls] = {}
        self.session.components[cls][name] = self

        self.session = session if session is not None else self.session
        self.name = name

    @classmethod
    def parse_cls(cls, d:dict, resources, session):
        "Parse a configuration dict to an instance"
        return cls(**d, session=session)