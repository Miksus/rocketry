
from powerbase.components import BaseComponent
from powerbase.config import parse_dict

import pytest

@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {
                "_pytest_component": {
                    "my-component-1": {
                        "x": 1, 
                        "y": 2,
                        "z": 3
                    },
                    "my-component-2": {
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
                "_pytest_component": [
                    {
                        "name": "my-component-1",
                        "x": 1, 
                        "y": 2,
                        "z": 3,
                    },
                    {
                        "name": "my-component-2",
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

    # Test a custom component
    class MyComponent(BaseComponent):
        __parsekey__ = "_pytest_component"
        
        def __init__(self, x, y, **kwargs):
            self.x, self.y = x, y
            super().__init__(**kwargs)

        @classmethod
        def parse_cls(cls, d: dict, **kwargs):
            assert 3 == d.pop("z")
            return super().parse_cls(d, **kwargs)

    assert {} == session.components
    parse_dict(config, session=session)

    for comp_name in ("my-component-1", "my-component-2"):
        comp = session.components[MyComponent][comp_name]
        assert isinstance(comp, MyComponent)
        assert 1 == comp.x
        assert 2 == comp.y
        assert not hasattr(comp, "z")
        assert comp.session is session