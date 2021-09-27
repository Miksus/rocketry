
import copy
from logging import Handler, LogRecord
from typing import List, Dict, Mapping, Union, TYPE_CHECKING

from ..formatters import AttributeFormatter

if TYPE_CHECKING:
    from pymongo.collection import Collection
    from pymongo.mongo_client import MongoClient

class MongoHandler(Handler):
    """A handler class which turns the logging records into
    dictionaries and then writes them to a Mongo database. 

    Parameters
    ----------
    collection : str, pymongo.collection.Collection
        Database collection where the records
        are saved.
    database : str
        Database name to use for logging. Not needed
        to specify if collection is pymongo Collection.
    client : str, pymongo.MongoClient, dict
        MongoDB client to use. Not needed to specify
        if collection is pymongo Collection.
        Assumed to be connection string if string
        and arguments for pymongo.MongoClient if 
        dict.
    **kwargs : dict
        Passed to logging.Handler.

    Examples
    --------

    >>> import pymongo # doctest: +SKIP
    >>> from redengine.log import MemoryHandler
    >>> client = pymongo.MongoClient('mongodb://localhost:27020') # doctest: +SKIP
    >>> handler = MongoHandler(client['mydb']['mycol']) # doctest: +SKIP

    Notes
    -----

    The connection object is created when needed and therefore one can safely
    change the connection string, database name or collection name before this.
    For example, if the connection string (especially the password) is desired to be 
    acquired after reading the configuration file, one can set the connection string 
    to a dummy string in the file and reset it with the correct value later.
    """
    
    # https://github.com/python/cpython/blob/aa92a7cf210c98ad94229f282221136d846942db/Lib/logging/__init__.py#L1119
    def __init__(self, collection:Union[str, 'Collection']=None, *, client:Union[str, 'MongoClient', dict]=None, database:str=None, **kwargs):
        super().__init__(**kwargs)
        
        self.client = client
        self.database = database
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
        self.col_object.insert_one(json)

    def read(self, **kwargs) -> List[Dict]:
        yield from self.col_object.find({})
        
    def clear_log(self):
        "Empty the collection."
        self.col_object.delete_many({})
        
    def _initiated(self):
        return hasattr(self, "_col_object")

    def _update_connection(self):
        import pymongo
        client = self.client
        database = self.database
        collection = self.collection

        if isinstance(client, str):
            client = pymongo.MongoClient(client)
        elif isinstance(client, Mapping):
            client = pymongo.MongoClient(**client)
        else:
            client = client
        self._col_object = client[database][collection]

    @property
    def col_object(self) -> 'Collection':
        if not self._initiated():
            self._update_connection()
        return self._col_object

    @property
    def collection(self) -> str:
        return self._collection
    
    @collection.setter
    def collection(self, item:Union['Collection', str]):
        if isinstance(item, str):
            self._collection = item
            if self._initiated():
                self._update_connection()
        else:
            self._collection = item.name
            self._database = item.database.name
            self._col_object = item

    @property
    def database(self) -> str:
        return self._database

    @database.setter
    def database(self, item:str):
        self._database = item
        if self._initiated():
            self._update_connection()

    @property
    def client(self) -> Union['MongoClient', str, dict]:
        return self._client

    @client.setter
    def client(self, item:Union[str, 'MongoClient', dict]):
        self._client = item
        if self._initiated():
            self._update_connection()
