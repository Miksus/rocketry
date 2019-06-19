

class ETLError(Exception):
    "Major error occured during the ETL process and the process should be ceased"

class SkipBatchException(Exception):
    "Error occured in Data Batch and it should be dropped"

class SkipTransformerException(Exception):
    "The transformer should be skipped"