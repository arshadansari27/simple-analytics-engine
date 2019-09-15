import pytest
import pytz
import copy
from datetime import datetime

from ..services import *
from ..config import RepositoryFactory, PROJECT_REPOSITORY, EVENT_REPOSITORY
from .fixtures.impls import InmemoryProjectRepository, InmemoryAnalyticalRepository
from .fixtures.data import ANALYTICAL_EVENTS, PROJECTS



@pytest.fixture()
def context():
    RepositoryFactory[EVENT_REPOSITORY] = InmemoryAnalyticalRepository(copy.copy(ANALYTICAL_EVENTS))
    RepositoryFactory[PROJECT_REPOSITORY] =  InmemoryProjectRepository(copy.copy(PROJECTS))
    _context = {
        'uri': 'tset/uri',
        'project_id': 32,
        'project_name': 'test_project',
        'project_description': 'asomslafmlasf lkasnf ladsjflasjf',
        'event_type': 'Type 1',
        'timestamp': datetime.now(pytz.UTC),
    }
    return _context

def test_add_event(context):
    uri, event_type, timestamp = context['uri'], context['event_type'], context['timestamp']
    project_id = 2
    event = add_event(uri, project_id, event_type, timestamp)
    assert RepositoryFactory[EVENT_REPOSITORY].get_by_id(event.event_id) is not None


def test_add_project(context):
    project_name, project_description = context['project_name'], context['project_description']
    print(add_project(project_name, project_description))


def test_get_events(context):
    project_id = 1
    timestamp = context['timestamp']
    print(get_events(project_id, timestamp))


def test_get_projects(context):
    assert len(get_projects()) == 2
