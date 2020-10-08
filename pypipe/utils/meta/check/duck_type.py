

"""
Utility checks containing duck type checks (quacks like a duck, its a duck)
"""

def is_filelike(value):
    """Is file-like object
    
    See: https://stackoverflow.com/a/1661354/13696660"""
    return hasattr(value, "read")