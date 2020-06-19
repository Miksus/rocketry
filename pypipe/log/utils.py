
import pandas as pd

def read_logger(logger, **kwargs):
        handlers = logger.handlers
        for handler in handlers:
            if hasattr(handler, "read"):
                df = pd.DataFrame(handler.read())
                return df
        else:
            raise AttributeError("No handlers that could read the logs (missing method 'read')")