from sqlalchemy import create_engine, MetaData 
from .sql import AnalyticalEventMysqlRepository, ProjectMysqlRepository
from ..models import AnalyticalEvent, Project
from collections import namedtuple
from datetime import datetime
import pytz
import pytest
import os
import json


@pytest.fixture
def context():
    try:
        os.remove('event_test.db')
    except FileNotFoundError:
        pass
    metadata = MetaData()
    engine = create_engine(f"sqlite:///event_test.db")
    EventRepositoryTuple = namedtuple("EventRepositoryTuple", ['event_repository', 'project_repository'])
    ae = AnalyticalEventMysqlRepository(metadata, engine)
    pr = ProjectMysqlRepository(metadata, engine)
    ctx = EventRepositoryTuple(ae, pr)
    metadata.create_all(engine)
    return ctx


def test_sql(context):
    event_repository = context.event_repository
    project_repository = context.project_repository
    projects = []
    events = []
    projects.append(Project(1, 1, "test project 1", "test description 1"))
    projects.append(Project(1, 2, "test project 2", "test description 2"))
    projects.append(Project(2, 3, "test project 3", "test description 3"))
    projects.append(Project(2, 4, "test project 4", "test description 4"))
    events.append(AnalyticalEvent(1, datetime(2019, 1, 1, 1, tzinfo=pytz.UTC), "event_type_1",  "/test-uri-1", "test description 1", 1))
    events.append(AnalyticalEvent(2, datetime(2019, 1, 1, 2, tzinfo=pytz.UTC), "event_type_1",  "/test-uri-1", "test description 1", 2))
    events.append(AnalyticalEvent(3, datetime(2019, 1, 2, tzinfo=pytz.UTC), "event_type_2",  "/test-uri-2", "test description 2", 3))
    events.append(AnalyticalEvent(4, datetime(2019, 1, 3, tzinfo=pytz.UTC), "event_type_2",  "/test-uri-2", "test description 2", 4))
    events.append(AnalyticalEvent(5, datetime(2019, 1, 4, tzinfo=pytz.UTC), "event_type_1",  "/test-uri-1", "test description 1", 1))
    events.append(AnalyticalEvent(6, datetime(2019, 1, 5, tzinfo=pytz.UTC), "event_type_1",  "/test-uri-1", "test description 1", 2))
    events.append(AnalyticalEvent(7, datetime(2019, 1, 6, tzinfo=pytz.UTC), "event_type_2",  "/test-uri-2", "test description 2", 3))
    events.append(AnalyticalEvent(8, datetime(2019, 1, 7, tzinfo=pytz.UTC), "event_type_2",  "/test-uri-2", "test description 2", 4))

    for project in projects:
        assert project_repository.upsert(project) == project.id

    project = project_repository.get_by_id(2)
    assert project.user_id == 1 and project.name == 'test project 2'
    project.user_id = 5 
    project_repository.upsert(project)
    project = project_repository.get_by_id(2)
    assert project.user_id == 5 and project.name == 'test project 2'
    projects = len([u for u in project_repository.get_all(5)]) == 1

    for event in events:
        project = project_repository.get_by_id(event.project_id)
        assert event_repository.add(event) == event.id

    event = event_repository.get_by_id(3)
    assert event.event_type == 'event_type_2' and event.project_id == 3
    events = event_repository.get_all_for_project(3, None, None)
    assert len([u for u in events]) == 2

    os.remove('event_test.db')
