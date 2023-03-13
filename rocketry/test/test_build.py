import pytest
import rocketry

def test_build(request):
    verify_build = request.config.getoption('check_build')
    if not verify_build:
        pytest.skip(reason="Pass '--check-build' to verify the package is built")
    assert rocketry.version != '0.0.0.UNKNOWN'