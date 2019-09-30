import pytest
import copy
from datetime import datetime, timedelta
from itertools import chain

from .services import EventService, StatService
from .models import AnalyticalEvent, Project, EventStats
from .repositories import AnalyticalEventRepository, ProjectRepository, EventStatsRepository
from .helper import generate_interval, generate_interval_range
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

class InMemoryEventStatsRepository(EventStatsRepository):

    def __init__(self, stats):
        self.stats = {self._key(s): s for s in stats}

    def _key(self, stat):
        it = int(stat.interval.timestamp())
        return f"{stat.period}-{it}-{stat.project_id}"
    
    def _key_ids(self, project_id, period, interval):
        it = int(interval.timestamp())
        return f"{period}-{it}-{project_id}"

    def upsert_event_stat(self, event_stat):
        existing_event_stat = self.stats.get(self._key(event_stat))
        if not existing_event_stat:
            self.stats[self._key(event_stat)] = event_stat
        else:
            existing_event_stat.count_total = event_stat.count_total
            existing_event_stat.count_event_types = event_stat.count_event_types
            existing_event_stat.count_uris = event_stat.count_uris

    def get_project_stats(self, project_id, period, timestamp_from, timestamp_to):
        if timestamp_from == timestamp_to:
            interval = generate_interval(period, timestamp_from)
            stats = [self.stats.get(self._key_ids(project_id, period, interval))]
        else:
            intervals = generate_interval_range(period, timestamp_from, timestamp_to)
            stats = []
            for interval in intervals:
                stat = self.stats.get(self._key_ids(project_id, period, interval))
                if not stat:
                    continue
                stats.append(stat)
        return [s for s in stats if s]
        

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
    AnalyticalEvent(1, datetime(2018, 12, 1, 8, 22, 33, tzinfo=pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(2, datetime(2019, 1, 1, 4, 22, 33, tzinfo=pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(3, datetime(2019, 2, 1, 3, 22, 33, tzinfo=pytz.UTC), 'TYPE 3', '/test-uri-2', 'test descripton', 1),
    AnalyticalEvent(4, datetime(2019, 3, 1, 13, 22, 33, tzinfo=pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(5, datetime(2019, 3, 15, 1, 22, 33, tzinfo=pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(6, datetime(2019, 3, 16, 11, 22, 33, tzinfo=pytz.UTC), 'TYPE 2', '/test-uri-2', 'test descripton', 2),
]
PROJECTS = [
        Project(1, 1, 'test project 1', 'this is a test project to be used by fixtures'),
        Project(1, 2, 'test project 2', 'this is a test project to be used by fixtures'),
]


@pytest.fixture()
def stat_context_core():
    event_repository = InMemoryAnalyticalEventRepository(copy.copy(ANALYTICAL_EVENTS))
    project_repository=  InMemoryProjectRepository(copy.copy(PROJECTS))
    class User:
        def __init__(self, user_id):
            self.id = user_id

    user_getter = lambda user_id: User(user_id)
    stats_repository = InMemoryEventStatsRepository([])
    event_service = EventService(user_getter, project_repository, event_repository)
    stat_service = StatService(user_getter, project_repository, stats_repository)
    _context_core = {
        'event_service': event_service,
        'stat_service': stat_service
    }
    return _context_core


def test_stats(stat_context_core):
    stat_servive = stat_context_core['stat_service']
    for event in ANALYTICAL_EVENTS:
        stat_servive.add_event_stat(1, 1, event) 
    stats, project = stat_servive.get_project_stats(
        'monthly', 1, 1, datetime(2019, 1, 1, tzinfo=pytz.UTC), datetime(2019, 4, 1, tzinfo=pytz.UTC))
    for stat in stats:
        if stat.interval != datetime(2019, 3, 1, tzinfo=pytz.UTC):
            continue
        assert stat.count_total is 3
        assert len(stat.count_event_types) is 2
        assert len(stat.count_uris) is 2