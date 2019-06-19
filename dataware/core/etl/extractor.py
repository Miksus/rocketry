
from .base import ETLBase

class ExtractorBase(ETLBase):

    """
    Methods:
    --------
        extract(): extract data
        extract_next(): extract next batch of data
            must have yield for the next batch
    """

    def __init__(self):
        pass

    @property
    def is_batch(self):
        return hasattr(self, "extract_next")

    def extract(self):
        return data

    def __iter__(self):
        return self

    def __next__(self):
        yield from self.extract_next()