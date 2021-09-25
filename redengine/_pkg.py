
import sys

def raise_for_missing_imports(*args):
    missing = [pkg for pkg in args if pkg not in sys.modules]
    raise ImportError(f"Missing packages: {missing}")