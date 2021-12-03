

class CondParser:
    "Utility class for parsing a condition item"
    cache = {}
    def __init__(self, func, cached=False):
        self.func = func
        self.cached = cached
    
    def __call__(self, s:str, *args, **kwargs):
        from redengine.core.condition import BaseCondition
        session = BaseCondition.session
        if self.cached and s in session.cond_cache:
            return session.cond_cache[s]

        cond = self.func(*args, **kwargs)
        if self.cached:
            session.cond_cache[s] = cond
        return cond