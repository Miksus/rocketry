
import logging
import csv
import io
import os
import copy
from logging import Formatter, FileHandler, Handler, LogRecord
from pathlib import Path
from typing import List, Dict
from dateutil.parser import parse as parse_datetime

from ..formatters import AttributeFormatter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pymongo.collection import Collection

class MongoHandler(Handler):
    """A handler class which turns the logging records to
    dictionaries and then writes them to a Mongo database. 

    Parameters
    ----------
    collection : pymongo.collection.Collection
        Database collection where the records
        are saved.

    Examples
    --------

    >>> import pymongo # doctest: +SKIP
    >>> from redengine.log import MemoryHandler
    >>> client = pymongo.MongoClient('mongodb://localhost:27020') # doctest: +SKIP
    >>> handler = MongoHandler(client['mydb']['mycol']) # doctest: +SKIP
    """
    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, collection:'Collection', **kwargs):
        super().__init__(**kwargs)
        self.collection = collection

        if self.formatter is None:
            self.formatter = AttributeFormatter()
        
    def emit(self, record:LogRecord):
        record = self.format(record)
        record = copy.copy(record)

        # Removing non picklable
        record.exc_info = None
        record.args = None

        json = vars(record)
        self.collection.insert_one(json)

    def read(self, **kwargs) -> List[Dict]:
        yield from self.collection.find({})
        
    def clear_log(self):
        "Empty the collection."
        self.collection.delete_many({})
