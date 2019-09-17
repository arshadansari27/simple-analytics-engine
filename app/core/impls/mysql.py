from ..repositories import AnalyticalEventRepository, ProjectRepository
from ..models import AnalyticalEvent, Project
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, String, Column, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy import insert, select, update


engine = create_engine('sqlite:///main.db')
metadata = MetaData()
projects = Table('projects', metadata,
    Column('id', Integer(), primary_key=True),
    Column('user_id', Integer(), nullable=False),
    Column('name', String(200),  nullable=False),
    Column('description', String(200),  nullable=True),
)
analytical_events = Table('analytical_events', metadata,
    Column('id', Integer(), primary_key=True),
    Column('uri', String(200), nullable=False),
    Column('event_type', String(20),  nullable=False),
    Column('description', String(200),  nullable=True),
    Column('timestamp', DateTime(), default=datetime.now, onupdate=datetime.now),
    Column('project_id', Integer(), ForeignKey(projects.c.id)),
)


@contextmanager
def transactional():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
        connection = None


class AnalyticalEventMysqlRepository(AnalyticalEventRepository):

    def generate_id(self):
        raise NotImplementedError

    def get_all_for_project(self, project_id, timestamp_from, timestamp_to):
        with transactional() as connection:
            dd = select([analytical_events]).where(analytical_events.c.project_id==project_id)
            if timestamp_from:
                dd = dd.where(analytical_events.c.timestamp <= timestamp_to)
            if timestamp_to:
                dd = dd.where(analytical_events.c.timestamp >= timestamp_from)
            rows = connection.execute(dd).fetchall()
            return (self._to_object(row) for row in rows)

    def get_by_id(self, event_id):
        with transactional() as connection:
            dd = select([analytical_events]).where(analytical_events.c.id==event_id)
            return self._to_object(connection.execute(dd).first())

    def add(self, event):
        with transactional() as connection:
            t = connection.begin()
            r = connection.execute(insert(analytical_events).values( **self._from_object(event)))
            t.commit()
            return r.inserted_primary_key[0]

    def _to_object(self, row):
        if not row:
            return None
        return AnalyticalEvent(row['id'], row['timestamp'], row['event_type'], row['uri'], row['description'], row['project_id'])

    def _from_object(self, event_object):
        return dict(
                id=event_object.id, 
                timestamp=event_object.timestamp, 
                event_type=event_object.event_type, 
                uri=event_object.uri, 
                description=event_object.description, 
                project_id=event_object.project_id)

class ProjectMysqlRepository(ProjectRepository):

    def generate_id(self):
        raise NotImplementedError

    def get_by_id(self, project_id):
        with transactional() as connection:
            dd = select([projects]).where(projects.c.id==project_id)
            return self._to_object(connection.execute(dd).first())

    def get_all(self, user_id):
        with transactional() as connection:
            dd = select([projects]).where(projects.c.user_id==user_id)
            rows = connection.execute(dd).fetchall()
            return (self._to_object(row) for row in rows)

    def upsert(self, project):
        with transactional() as connection:
            t = connection.begin()
            existing_project = self.get_by_id(project.id)
            if not existing_project:
                r = connection.execute(insert(projects).values(**self._from_object(project)))
                t.commit()
                return r.inserted_primary_key[0]
            existing_project.user_id = project.user_id
            existing_project.name = project.name
            existing_project.description = project.description
            rows_updated = connection.execute(update(projects).where(
                projects.c.id==project.id).values(**self._from_object(existing_project)))
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

metadata.create_all(engine)
