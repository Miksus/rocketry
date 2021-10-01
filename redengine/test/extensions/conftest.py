
from redengine import Session

class ExtensionBase:

    def test_parse_name_dict(self, session, config):
        assert {} == session.extensions
        Session.from_dict(config)