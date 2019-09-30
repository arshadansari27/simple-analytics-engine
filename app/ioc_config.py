from sqlalchemy import create_engine, MetaData 
from .core.services import EventService, StatService
from .auth.services import AuthService
from .core.impls.sql import AnalyticalEventMysqlRepository, ProjectMysqlRepository
from .core.impls.mongo import EventStatsMongoRepository
from .auth.impls.sql import AuthorisationSQLRepository, UserSQLRepository
from collections import namedtuple


Context = namedtuple("Context", ['event_service', 'auth_service', 'stats_service'])


def create_context(db_name):
    metadata = MetaData()
    engine = create_engine(f"sqlite:///{db_name}")
    mongo_client = None

    user_repository = UserSQLRepository(metadata, engine)
    auth_repository = AuthorisationSQLRepository(metadata, engine)
    auth_service = AuthService(user_repository, auth_repository)

    user_getter = user_repository.get_by_id
    project_repository = ProjectMysqlRepository(metadata, engine)
    analytical_repository = AnalyticalEventMysqlRepository(metadata, engine)
    stats_repository = EventStatsMongoRepository(mongo_client)
    event_service = EventService(user_getter, project_repository, analytical_repository)
    stats_service = StatService(user_getter, project_repository, stats_repository)    
    metadata.create_all(engine)
    return Context(event_service, auth_service, stats_service)


