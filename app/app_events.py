

HANDLERS = {}


def register(key, handler):
    HANDLERS[key] = handler

def unregister(key):
    del HANDLERS[key]

def poke(key, *args, **kwargs):
    if key not in HANDLERS:
        print(f"No handler registered for {key}")
        return
    HANDLERS[key](*args, **kwargs)

