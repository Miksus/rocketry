
import logging
import csv
import io
import os
import copy
from logging import Formatter, FileHandler, Handler
from pathlib import Path
from typing import List, Dict
from dateutil.parser import parse as parse_datetime

from ..formatters import AttributeFormatter

class MongoHandler(Handler):
    """
    Logging handler to log records to a Mongo database.
    """
    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, collection, **kwargs):
        """Initialize MongoHandler

        Parameters
        ----------
        collection : pymongo.Collection, optional
            Collection where the records are stored
        """
        super().__init__(**kwargs)
        self.collection = collection

        if self.formatter is None:
            self.formatter = AttributeFormatter()
        
    def emit(self, record):
        record = self.format(record)
        record = copy.copy(record)

        # Removing non picklable
        record.exc_info = None
        record.args = None

        json = vars(record)
        self.collection.insert_one(json)
# Extras
    def read(self, **kwargs) -> List[Dict]:
        "Read the log file as pandas dataframe"
        yield from self.collection.find({})
        
    def clear_log(self):
        "Empty the collection"
        self.collection.delete_many({})
