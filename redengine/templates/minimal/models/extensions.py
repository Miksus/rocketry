
# Extensions for tasks
import re
from redengine.core import BaseExtension

class MyExtension(BaseExtension):
    """My extension class"""
    __parsekey__ = 'myextensions'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
