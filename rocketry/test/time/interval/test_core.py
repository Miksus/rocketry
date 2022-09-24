
import pytest
from rocketry.core.time.anchor import AnchoredInterval

# Test no unexpected errors in all
@pytest.mark.parametrize("method", ["__str__", "__repr__"])
@pytest.mark.parametrize("cls", AnchoredInterval.__subclasses__())
def test_magic_noerror(method, cls):
    obj = cls()
    getattr(obj, method)()
