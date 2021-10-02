
# Extensions for tasks
import re
from redengine.core import BaseExtension

class MyExtension(BaseExtension):
    """My extension class"""

    # Parsekey is used in Session.from_dict
    # so that custom extensions can be 
    # used in configuration.
    __parsekey__ = 'myextensions'

    def at_parse(self, **kwargs):
        # What the extension does...
        ...

    def delete(self):
        # How the extension is deleted.
        super().delete()