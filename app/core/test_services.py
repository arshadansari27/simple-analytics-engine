import pytest
import copy
from datetime import datetime, timedelta

from .services import EventService
from .models import AnalyticalEvent, Project
from .repositories import AnalyticalEventRepository, ProjectRepository
from datetime import datetime
import pytz


class InMemoryAnalyticalEventRepository(AnalyticalEventRepository):

    def __init__(self, events):
        self.events = events

    def generate_id(self):
        return (max(u.id for u in self.events) + 1) if not self.events else 1
    
    def get_all_for_project(self, project_id, timestamp_from, timestamp_to):
        return [u for u in self.events if u.id == project_id and u.timestamp <= timestamp_to and u.timestamp >= timestamp_from] 
    
    def get_by_id(self, event_id):
        try:
            return next((u for u in self.events if u.id == event_id ))
        except StopIteration:
            return None

    def add(self, event):
        if not event.id:
            event.event = self.generate_id()
        self.events.append(event)
        return event.id


class InMemoryProjectRepository(ProjectRepository):

    def __init__(self, projects):
        self.projects = projects

    def generate_id(self):
        return (max(u.id for u in self.projects) + 1) if self.projects else 1

    def get_by_id(self, project_id):
        try:
            return next((u for u in self.projects if u.id == project_id))
        except StopIteration:
            return None

    def get_all(self, user_id):
        return [u for u in self.projects]

    def upsert(self, project):
        if project.id:
            try:
                _project = next((u for u in self.projects if u.id == project.id ))
                for key in _project.__dict__:
                    _project.__dict__[key] = getattr(project, key, None)
                return _project
            except StopIteration:
                pass
        if not project.id:
            project.id = self.generate_id()
        self.projects.append(project)
        return project.id
 


@pytest.fixture()
def context_core():
    event_repository = InMemoryAnalyticalEventRepository(copy.copy(ANALYTICAL_EVENTS))
    project_repository=  InMemoryProjectRepository(copy.copy(PROJECTS))
    class User:
        def __init__(self, user_id):
            self.id = user_id

    user_getter = lambda user_id: User(user_id)
    event_service = EventService(user_getter, project_repository, event_repository)
    _context_core = {
        'uri': 'tset/uri',
        'project_id': 32,
        'project_name': 'test_project',
        'project_description': 'asomslafmlasf lkasnf ladsjflasjf',
        'event_type': 'Type 1',
        'timestamp': datetime.now(pytz.UTC),
        'event_service': event_service
    }
    return _context_core


def test_add_event(context_core):
    event_service = context_core['event_service']
    uri, event_type, timestamp = context_core['uri'], context_core['event_type'], context_core['timestamp']
    project_id = 2
    event_id = event_service.add_event(1, project_id, timestamp, event_type, uri, 'test description')
    assert event_service.event_repository.get_by_id(event_id) is not None


def test_add_project(context_core):
    event_service = context_core['event_service']
    project_name, project_description = context_core['project_name'], context_core['project_description']
    project_id = event_service.add_project(1, project_name, project_description)
    assert project_id is not None and project_id > 0


def test_get_events(context_core):
    event_service = context_core['event_service']
    project_id = 1
    timestamp = context_core['timestamp']
    print(event_service.get_all_events(project_id, timestamp - timedelta(days=1), timestamp + timedelta(days=1)))


def test_get_projects(context_core):
    event_service = context_core['event_service']
    assert len(event_service.get_all_projects(1)) == 2



ANALYTICAL_EVENTS = [
    AnalyticalEvent(1, datetime.now(pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(2, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(3, datetime.now(pytz.UTC), 'TYPE 3', '/test-uri-2', 'test descripton', 1),
    AnalyticalEvent(4, datetime.now(pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(5, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(6, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-2', 'test descripton', 2),
]
PROJECTS = [
        Project(1, 1, 'test project 1', 'this is a test project to be used by fixtures'),
        Project(1, 2, 'test project 2', 'this is a test project to be used by fixtures'),
]


