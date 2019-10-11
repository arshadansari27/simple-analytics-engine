"""SQL Repository"""

from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table, Text, insert, select, update)

import dateutil
from ..models import AnalyticalEvent, Project
from ..repositories import (AnalyticalEventRepository, ProjectRepository)


@contextmanager
def transactional(engine):
    """
    Transactional Context
    """
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
        connection = None


class ProjectMysqlRepository(ProjectRepository):
    """
    Project Respository for Mysql
    """

    projects = None 

    @classmethod
    def create_table_schema(cls, metadata):
        '''
        Create table schema
        '''
        if cls.projects is not None:
            return
        cls.projects = Table('projects', metadata,
            Column('id', Integer(), primary_key=True),
            Column('user_id', Integer(), nullable=False),
            Column('name', String(200),  nullable=False),
            Column('description', String(200),  nullable=True),
        )

    def __init__(self, metadata, engine):
        self.engine = engine

    def generate_id(self):
        with transactional(self.engine) as connection:
            data = connection.execute("select max(id) from projects").fetchone()[0]
            if not data:
                return 1
            return int(data) + 1

    def get_by_id(self, project_id):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.projects]).where(self.__class__.projects.c.id==project_id)
            return self._to_object(connection.execute(dd).first())

    def get_all(self, user_id):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.projects]).where(self.__class__.projects.c.user_id==user_id)
            rows = connection.execute(dd).fetchall()
            return (self._to_object(row) for row in rows)

    def upsert(self, project):
        with transactional(self.engine) as connection:
            t = connection.begin()
            existing_project = self.get_by_id(project.id)
            if not existing_project:
                r = connection.execute(insert(self.__class__.projects).values(**self._from_object(project)))
                t.commit()
                return r.inserted_primary_key[0]
            existing_project.user_id = project.user_id
            existing_project.name = project.name
            existing_project.description = project.description
            rows_updated = connection.execute(update(self.projects).where(
                self.__class__.projects.c.id==project.id).values(**self._from_object(existing_project)))
            if rows_updated:
                t.commit()
                return existing_project.id
            raise Exception("Something went wrong")
    
    def _from_object(self, project):
        return dict(user_id=project.user_id, id=project.id, name=project.name, description=project.description)

    def _to_object(self, row):
        if not row:
            return None
        return Project(row['user_id'], row['id'], row['name'], row['description'])

class AnalyticalEventMysqlRepository(AnalyticalEventRepository):

    analytical_events = None

    @classmethod
    def create_table_schema(cls, metadata):
        if cls.analytical_events is not None:
            return
        if ProjectMysqlRepository.projects is None:
            ProjectMysqlRepository.create_table_schema(metadata)
        cls.analytical_events = Table('analytical_events', metadata,
            Column('id', Integer(), primary_key=True),
            Column('uri', String(200), nullable=False),
            Column('event_type', String(20),  nullable=False),
            Column('description', String(200),  nullable=True),
            Column('timestamp', DateTime(), default=datetime.now, onupdate=datetime.now),
            Column('project_id', Integer(), ForeignKey(ProjectMysqlRepository.projects.c.id)),
        )

    def __init__(self, metadata, engine):
        self.__class__.create_table_schema(metadata)
        self.engine = engine

    def generate_id(self):
        with transactional(self.engine) as connection:
            value = connection.execute("select max(id) from analytical_events").scalar()
            if not value:
                return 1
            return int(value) + 1

    def get_all_for_project(self, project_id, timestamp_from, timestamp_to):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.analytical_events]).where(self.__class__.analytical_events.c.project_id==project_id)
            if timestamp_from:
                dd = dd.where(self.__class__.analytical_events.c.timestamp.bool_op('<=')(timestamp_to))
            if timestamp_to:
                dd = dd.where(self.__class__.analytical_events.c.timestamp.bool_op('>=')(timestamp_from))
            rows = connection.execute(dd).fetchall()
            return (self._to_object(row) for row in rows)

    def get_by_id(self, event_id):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.analytical_events]).where(self.__class__.analytical_events.c.id==event_id)
            return self._to_object(connection.execute(dd).first())

    def add(self, event):
        with transactional(self.engine) as connection:
            t = connection.begin()
            r = connection.execute(insert(self.__class__.analytical_events).values( **self._from_object(event)))
            t.commit()
            return r.inserted_primary_key[0]

    def _to_object(self, row):
        if not row:
            return None
        ts = row['timestamp']
        if isinstance(ts, str):
            ts = dateutil.parser.parse(ts)
        return AnalyticalEvent(row['id'], ts, row['event_type'], row['uri'], row['description'], row['project_id'])

    def _from_object(self, event_object):
        return dict(
                id=event_object.id, 
                timestamp=event_object.timestamp, 
                event_type=event_object.event_type, 
                uri=event_object.uri, 
                description=event_object.description, 
                project_id=event_object.project_id)
