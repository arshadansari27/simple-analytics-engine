from sqlalchemy import create_engine, MetaData 
from .core.services import EventService
from .core.impls.sql import AnalyticalEventMysqlRepository, ProjectMysqlRepository
from collections import namedtuple


Context = namedtuple("Context", ['event_service', 'auth_service', 'project_repository', 'event_repository', 'user_getter'])

def create_context(db_name, user_getter):
    metadata = MetaData()
    engine = create_engine(f"sqlite:///{db_name}")
    project_repository = ProjectMysqlRepository(metadata, engine)
    analytical_repository = AnalyticalEventMysqlRepository(metadata, engine)
    event_service = EventService(user_getter, project_repository, analytical_repository)
    metadata.create_all(engine)
    return Context(event_service, None, project_repository, analytical_repository, user_getter)


