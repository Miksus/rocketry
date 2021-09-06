
from redengine.config import parse_dict

class ExtensionBase:

    def test_parse_name_dict(self, session, config):
        assert {} == session.extensions
        parse_dict(config)