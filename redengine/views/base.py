from redengine.session import Session

def register_view(name:str):
    def wrapper(cls):
        setattr(Session, name, property(cls)) 
    return wrapper