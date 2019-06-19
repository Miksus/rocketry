

class LoaderBase(ETLBase):
    """[summary]

    Methods:
    --------
        stage(data): stage data (before loading it to target)
        commit(): load data to target

        load(data): load data to target
        
        set_up(): run before starting to extract data
        clean_up(): run after all is finished
    """
    def stage(self, data):
        "Load data to target"
        raise NotImplementedError

    def set_up(self):
        "Setup loader before starting to extract data"
        pass

    def clean_up(self):
        pass
    
    def commit(self):
        "Commit save after, does nothing by default"
        pass

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.commit()
