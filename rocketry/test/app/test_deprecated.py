import logging
import pytest
from rocketry import Rocketry

def test_set_logging():
    app = Rocketry(execution="async")
    with pytest.warns(DeprecationWarning):
        @app.set_logger()
        def set_logging(logger):
            assert isinstance(logger, logging.Logger)
