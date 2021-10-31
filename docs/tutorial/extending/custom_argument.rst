.. _cust-arg:

Custom Argument
================

Custom arguments can be made by subclassing 
:class:`redengine.core.BaseArgument`.

Here is a practical demonstration:

.. code-block:: python

    import yaml
    from redengime.core import BaseArgument

    class YamlArg(BaseArgument):
        "Argument which value is a key in an YAML file"
        def __init__(self, file, key):
            self.file = file
            self.key = key

        def get_value(self):
            with open(self.file, "r") as buf:
                cont = yaml.safe_load(buf))
            return cont[self.key]

        @classmethod
        def to_session(self, key, file):
            cls.session.parameters[key] = cls(file, key)

Then create a parameter from the argument:

.. code-block:: python

    YamlArg.to_session("mykey", "my_file.yaml")
