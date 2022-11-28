import pytest
import rocketry

def test_build(request):
    expect_build = request.config.getoption('is_build')
    if not expect_build:
        assert rocketry.version == '0.0.0.UNKNOWN'
    else:
        assert rocketry.version != '0.0.0.UNKNOWN'