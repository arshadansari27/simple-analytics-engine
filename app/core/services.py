from .repositories import AnalyticalEventRepository, ProjectRepository, EventStatsRepository
from .models import AnalyticalEvent, Project, EventStats
from .helper import generate_interval, generate_interval_range
from ..app_events import poke
import pytz


class EventService:

    def __init__(self, user_getter, 
            project_repository: ProjectRepository, 
            event_repository: AnalyticalEventRepository,
        ):
        self.project_repository = project_repository
        self.event_repository = event_repository
        self.user_getter = user_getter

    def get_all_projects(self, user_id):
        return self.project_repository.get_all(user_id)

    def add_project(self, user_id, project_name, project_description):
        user = self.user_getter(user_id)
        # TODO: Check user roles to see if user can add project
        project_id = self.project_repository.generate_id()
        project = Project(user.id, project_id, project_name, project_description)
        self.project_repository.upsert(project)
        return project.id

    def change_project_name(self, user_id, project_id, project_new_name):
        user = self.user_getter(user_id)
        # TODO: Check user roles to see if user can update project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFound(f"Project {project_id} not found")
        project.name = project_new_name
        self.project_repository.upsert(project)
        return project.id

    def update_project_description(self, user_id, project_id, project_description):
        user = self.user_getter(user_id)
        # TODO: Check user roles to see if user can update project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFound(f"Project {project_id} not found")
        project.description = project_description 
        self.project_repository.upsert(project)
        return project.id

    def get_project(self, project_id):
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFound(f"Project {project_id} not found")
        return project

    def get_all_events(self, project_id, timestamp_from, timestamp_to):
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFound(f"Project {project_id} not found")
        return self.event_repository.get_all_for_project(project.id, timestamp_from, timestamp_to)

    def add_event(self, user_id, project_id, timestamp, event_type, uri, description):
        user = self.user_getter(user_id)
        # TODO: Check user roles to see if user can update project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFound(f"Project {project_id} not found")
        event_id = self.event_repository.generate_id()
        event = AnalyticalEvent(event_id, timestamp, event_type, uri, description, project.id) 
        self.event_repository.add(event)
        poke('EVENT_ARRIVAL', user.id, project.id, event.id)
        return event.id

    def get_event(self, event_id):
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFound(f"Event {event_id} not found")
        return event


class StatService:

    def __init__(self, user_getter, project_repository: ProjectRepository, stats_repository: EventStatsRepository):
        self.user_getter = user_getter
        self.stats_repository = stats_repository
        self.project_repository = project_repository

    def add_event_stat(self, user_id, project_id, event):
        user = self.user_getter(user_id)
        project = self.project_repository.get_by_id(project_id)
        for period in EventStats.PERIODS:
            interval = generate_interval(period, event.timestamp.replace(tzinfo=pytz.UTC))
            event_stats = list(self.stats_repository.get_project_stats(project.id, period, interval, interval))
            if not event_stats:
                print("Creating new event stats")
                event_stat = EventStats(user.id, period, interval, project.id, 0, {}, {})
            else:
                print("Found existing event stats")
                assert len(event_stats) is 1
                event_stat = event_stats[0]
            print(event_stat.to_json())
            event_stat.count_total += 1
            if event.event_type in event_stat.count_event_types:
                event_stat.count_event_types[event.event_type] += 1
            else:
                event_stat.count_event_types[event.event_type] = 1
            if event.uri in event_stat.count_uris:
                event_stat.count_uris[event.uri] += 1
            else:
                event_stat.count_uris[event.uri] = 1
            self.stats_repository.upsert_event_stat(event_stat)

    def get_project_stats(self, period, user_id, project_id, timestamp_from, timestamp_to):
        project = self.project_repository.get_by_id(project_id)
        return  self.stats_repository.get_project_stats(project_id, period, timestamp_from, timestamp_to), project


class EventNotFound(Exception):
    pass


class ProjectNotFound(Exception):
    pass

