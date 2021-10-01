
from logging.config import dictConfig

def parse_logging(conf, **kwargs):
    dictConfig(conf)
