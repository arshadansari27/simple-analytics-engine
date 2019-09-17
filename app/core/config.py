from .services import EventService

def event_service_factory(user_getter):
    return EventService(user_getter, None, None)
