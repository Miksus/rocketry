
import logging

class FilterAll(logging.Filter):
    """Filter all records"""

    def filter(self, record):
        return False