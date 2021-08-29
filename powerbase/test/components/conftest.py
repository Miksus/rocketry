
from powerbase.config import parse_dict

class ComponentBase:

    def test_parse_name_dict(self, session, config):
        assert {} == session.components
        parse_dict(config)