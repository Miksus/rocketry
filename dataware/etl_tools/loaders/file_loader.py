

class FileLoader():

    write_funcs = {
        "csv": pd.to_csv,
        "json": pd.to_json,
        "html": pd.to_html,

        "xlsx": pd.to_excel,
        "xls": pd.to_excel,
        "xlm": pd.to_excel,

        "hdf": pd.to_hdf,

        "pickle": pd.to_pickle,
        "pkl": pd.to_pickle
    }

    read_funcs = {
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


    def __init__(self, target_path, target_kwds=None, stage_path=None, stage_kwds=None, delete_stage):
        self.target_path = target_path
        self.target_kwds = {} if target_kwds is None else target_kwds

        self.stage_path = stage_path
        self.stage_kwds = {} if stage_kwds is None else stage_kwds

    def stage(self, df):
        suffix = Path(self.file_path).suffix
        write_stage = self.write_funcs[get_suffix(self.stage_path)]
        write_stage(self._stage_file, **self.stage_kwds)
        
    def commit(self):
        read_stage = self.read_funcs[get_suffix(self.stage_path)]
        df = read_stage(self.stage_path, **self.stage_kwds)

        write_commit = self.write_funcs[get_suffix(self.target_path)]
        write_commit(self.target_path, **self.target_kwds)
        

    def setup(self):
        self._stage_file = open(self.stage_path, mode="a")

    def teardown(self):
        self._stage_file.close()

    def get_commit_func(self):
        suffix = Path(self.file_path).suffix
        return self.files_funcs[suffix]

    @property
    def is_batch(self):
        return self.stage_path is not None

def get_suffix(path):
    return Path(path).suffix