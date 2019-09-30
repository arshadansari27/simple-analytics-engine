from sqlalchemy import create_engine, MetaData 
from .core.services import EventService, StatService
from .auth.services import AuthService
from .core.impls.sql import AnalyticalEventMysqlRepository, ProjectMysqlRepository
from .core.impls.mongo import EventStatsMongoRepository
from .auth.impls.sql import AuthorisationSQLRepository, UserSQLRepository
from collections import namedtuple
import pymongo
from flask import Flask, request, jsonify
from celery import Celery



Context = namedtuple("Context", ['event_service', 'auth_service', 'stats_service'])


def create_context(config):
    global context
    print("[CONF]", config)
    db_name = config['db_name']
    #TODO: Uncomment and point to mysql db if not using sqlite
    #sql_host = config.get('sql_host')
    #sql_port = config.get('sql_port')
    mongo_host = config.get('mongo_host', 'localhost')
    mongo_port = config.get('mongol_port', 27017)
    metadata = MetaData()
    engine = create_engine(f"sqlite:///{db_name}.db")
    mongo_client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
    db = mongo_client[db_name]

    user_repository = UserSQLRepository(metadata, engine)
    auth_repository = AuthorisationSQLRepository(metadata, engine)
    auth_service = AuthService(user_repository, auth_repository)

    user_getter = user_repository.get_by_id
    project_repository = ProjectMysqlRepository(metadata, engine)
    analytical_repository = AnalyticalEventMysqlRepository(metadata, engine)

    stats_repository = EventStatsMongoRepository(db)

    event_service = EventService(user_getter, project_repository, analytical_repository)
    stats_service = StatService(user_getter, project_repository, stats_repository)    
    metadata.create_all(engine)
    app = create_app(config)
    context = Context(event_service, auth_service, stats_service)
    return context, app, create_celery(config, app)


def create_app(config):
    global app 
    config_broker_url = config.get('broker_url') or 'redis://localhost:6379/0'
    config_result_backend = config.get('broker_url') or 'redis://localhost:6379/0'
    _app = Flask('simple_analytics_engine')
    _app.config['CELERY_BROKER_URL'] = config_broker_url
    _app.config['CELERY_RESULT_BACKEND'] = config_result_backend
    app = _app
    return _app


def create_celery(config, app):
    global celery
    _celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    _celery.conf.update(app.config)
    celery = _celery
    return _celery


celery = None
app = None
context = None