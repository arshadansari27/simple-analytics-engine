from .core.services import EventService
from .core.impls.mysql import AnalyticalEventMysqlRepository, ProjectMysqlRepository


DB = 'main.db'


def event_service_prototype(user_getter):
    return EventService(user_getter, ProjectMysqlRepository(DB), AnalyticalEventMysqlRepository(DB))
