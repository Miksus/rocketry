
# Extensions for tasks
import re
from redengine.core import BaseExtension

class MyExtension(BaseExtension):
    """My extension class"""
    __parsekey__ = 'myextensions'

    def __init__(self, **kwargs):
        # What the extension does...
        super().__init__(**kwargs)

    def delete(self):
        # How the extension is deleted
        super().delete()