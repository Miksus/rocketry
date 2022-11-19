
import pickle

def is_pickleable(obj):
    try:
        pickle.dumps(obj)
    except Exception:
        return False
    else:
        return True
