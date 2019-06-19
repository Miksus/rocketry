
from dataflow.etl.extractor import Extractor
from pathlib import Path
import glob


class FileExtractor(Extractor):
    """Extractor for files. Automatic file recognizion.

    FileExtractor("dir/file.csv")
    FileExtractor"dir/file.csv")
    """

    files_funcs = {
        "csv": pd.read_csv,
        "json": pd.read_json,
        "html": pd.read_html,

        "xlsx": pd.read_excel,
        "xls": pd.read_excel,
        "xlm": pd.read_excel,

        "hdf": pd.read_hdf,

        "pickle": pd.read_pickle,
        "pkl": pd.read_pickle
    }

    glob_wildcards = {"*", '?'}

    def __init__(self, path, **kwargs):
        self.path = path
        self.kwds = kwargs

        # Test if file format can be extracted
        suffix = Path(self.file_path).suffix
        if suffix not in self.files_funcs:
            raise NotImplementedError(f"File extraction not implemented for {suffix}")

        # Execution time variables
        self.current_path = None

    def extract(self):
        func = self.get_extractor_func()
        self.current_path = self.path
        return func(self.path, **self.kwds)

    def extract_next(self):
        func = self.get_extractor_func()
        for filepath in glob.iglob(self.path, recursive=True):
            self.current_path = filepath
            if self.is_chuncked:
                yield from func(self.path, **self.kwds)
            else:
                yield func(self.path, **self.kwds)

    def get_extractor_func(self):
        suffix = Path(self.file_path).suffix
        return self.files_funcs[suffix]

    @property
    def is_batch(self):
        return self.has_path_wildcards or self.is_chuncked

    @property
    def has_path_wildcards(self):
        return any(
            wildcard in self.path 
            for wildcard in self.glob_wildcards
        )

    @property
    def is_chuncked(self):
        return "chunksize" in self.kwds
