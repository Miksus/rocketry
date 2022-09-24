def get_field_value(record, field:str):
    if isinstance(record, dict):
        return record[field]
    return getattr(record, field)
