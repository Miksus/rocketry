from redengine.core.parameters import Argument

class Private(Argument):
    "Argument that is not meant to be shown outside usage"

    string_hidden = "*****"

    def __init__(self, value):
        self.__value

    def get_value(self, task=None):
        if task is None:
            return self.string_hidden
        else:
            # Called for task --> must pass the actual value
            return self.__value

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}({self.string_hidden})'

    def __str__(self):
        return self.string_hidden