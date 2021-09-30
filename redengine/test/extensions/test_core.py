
import pytest

from redengine.extensions import BaseExtension
from redengine import Session

@pytest.mark.parametrize("global_session", [True, False], ids=["global session", "local session"])
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
def test_creation(session, config, global_session):
    config = config.copy()
    # Test a custom extension
    class MyExtension(BaseExtension):
        __parsekey__ = "_pytest_extension"
        
        def at_parse(self, x, y, **kwargs):
            self.x, self.y = x, y

        @classmethod
        def parse_cls(cls, d: dict, **kwargs):
            d_ext = d.copy()
            assert 3 == d_ext.pop("z")
            return super().parse_cls(d_ext, **kwargs)

    assert {} == session.extensions
    if global_session:
        Session.from_dict(config, session=session)
    else:
        session = Session.from_dict(config)

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