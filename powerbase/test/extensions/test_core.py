
from powerbase.extensions import BaseExtension
from powerbase.config import parse_dict

import pytest

@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {
                "_pytest_extension": {
                    "my-extension-1": {
                        "x": 1, 
                        "y": 2,
                        "z": 3
                    },
                    "my-extension-2": {
                        "x": 1, 
                        "y": 2,
                        "z": 3
                    },
                }
            },
            id="Dict of dicts (key as name)"
        ),
        pytest.param(
            {
                "_pytest_extension": [
                    {
                        "name": "my-extension-1",
                        "x": 1, 
                        "y": 2,
                        "z": 3,
                    },
                    {
                        "name": "my-extension-2",
                        "x": 1, 
                        "y": 2,
                        "z": 3,
                    },
                ]
            },
            id="List of dicts"
        ),
    ]
)
def test_creation(session, config):

    # Test a custom extension
    class MyExtension(BaseExtension):
        __parsekey__ = "_pytest_extension"
        
        def __init__(self, x, y, **kwargs):
            self.x, self.y = x, y
            super().__init__(**kwargs)

        @classmethod
        def parse_cls(cls, d: dict, **kwargs):
            assert 3 == d.pop("z")
            return super().parse_cls(d, **kwargs)

    assert {} == session.extensions
    parse_dict(config, session=session)

    for ext_name in ("my-extension-1", "my-extension-2"):
        comp = session.extensions["_pytest_extension"][ext_name]
        assert isinstance(comp, MyExtension)
        assert 1 == comp.x
        assert 2 == comp.y
        assert not hasattr(comp, "z")
        assert comp.session is session

def test_delete(session):
    # Test a custom extension
    class MyExtension(BaseExtension):
        __parsekey__ = "_pytest_extension"
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
    
    ext = MyExtension(name="my-extension")
    assert session.extensions["_pytest_extension"] == {"my-extension": ext}
    ext.delete()
    assert session.extensions["_pytest_extension"] == {}