import pytest
import pytz
import copy
from datetime import datetime, timedelta

from ..services import EventService
from .fixture_impls import InMemoryProjectRepository, InMemoryAnalyticalEventRepository, ANALYTICAL_EVENTS, PROJECTS



@pytest.fixture()
def context():
    event_repository = InMemoryAnalyticalEventRepository(copy.copy(ANALYTICAL_EVENTS))
    project_repository=  InMemoryProjectRepository(copy.copy(PROJECTS))
    class User:
        def __init__(self, user_id):
            self.id = user_id

    user_getter = lambda user_id: User(user_id)
    event_service = EventService(user_getter, project_repository, event_repository)
    _context = {
        'uri': 'tset/uri',
        'project_id': 32,
        'project_name': 'test_project',
        'project_description': 'asomslafmlasf lkasnf ladsjflasjf',
        'event_type': 'Type 1',
        'timestamp': datetime.now(pytz.UTC),
        'event_service': event_service
    }
    return _context


def test_add_event(context):
    event_service = context['event_service']
    uri, event_type, timestamp = context['uri'], context['event_type'], context['timestamp']
    project_id = 2
    event_id = event_service.add_event(1, project_id, timestamp, event_type, uri, 'test description')
    assert event_service.event_repository.get_by_id(event_id) is not None


def test_add_project(context):
    event_service = context['event_service']
    project_name, project_description = context['project_name'], context['project_description']
    project_id = event_service.add_project(1, project_name, project_description)
    assert project_id is not None and project_id > 0


def test_get_events(context):
    event_service = context['event_service']
    project_id = 1
    timestamp = context['timestamp']
    print(event_service.get_all_events(project_id, timestamp - timedelta(days=1), timestamp + timedelta(days=1)))


def test_get_projects(context):
    event_service = context['event_service']
    assert len(event_service.get_all_projects(1)) == 2

