

class Selector():

    def __init__(self, columns=None, indices=None, positional=False):

        self.columns = slice(None) if columns is None else columns
        self.indices = slice(None) if indices is None else indices
        
        self.positional = positional

    def transform(self, df):
        if self.positional:
            return df.iloc[self.indices, self.column]
        else:
            return df.loc[self.indices, self.column]
