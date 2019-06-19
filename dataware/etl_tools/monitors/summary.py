

class SummaryMonitor():

    def __init__(self):
        pass


    def inspect(self, df):
        string = (
            "Monitor\n"
            "-------\n"
            '\n'
            "Shape:\n"
            f"  Columns: {data.shape[1]}\n"
            f"  Rows: {data.shape[0]}\n"
            '\n'
            "Index:\n"
            f"  Type: {type(data.index)}\n"
            "   Span:\n"
            f"      Min: {data.index.min()}\n"
            f"      Max: {data.index.max()}\n"
            "   Values:\n"
            f"      Uniques: {data.index.nunique()}\n"
            f"      Nulls: {data.index.isnull().sum()}\n"
            "Columns:\n"
            f"  Names: {data.columns.tolist()}\n"
            f"  Types: {data.dtypes.tolist()}\n"
            '\n'
            "Describe:\n"
            f"{data.describe()}"


        )
        return string