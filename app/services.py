from .models import AnalyticalEvent, Project
from .config import RepositoryFactory, PROJECT_REPOSITORY, EVENT_REPOSITORY

def add_event(uri, project_id, event_type, timestamp):
    project_repository = RepositoryFactory.get(PROJECT_REPOSITORY)
    project = project_repository.get_by_id(project_id)
    return project.create_event(event_type, uri, timestamp, 'some description')


def add_project(project_name, project_description):
    project_repository = RepositoryFactory.get(PROJECT_REPOSITORY)
    project = Project(project_repository.get_new_id(), project_name, project_description)
    project_repository.upsert(project)
    return project.project_id

def get_events(project_id, timestamp):
    project_repository = RepositoryFactory.get(PROJECT_REPOSITORY)
    event_repository = RepositoryFactory.get(EVENT_REPOSITORY)
    project = project_repository.get_by_id(project_id)
    if not project:
        raise ProjectNotFound()
    return event_repository.get_all_for_project(project.project_id, timestamp)

def get_projects():
    project_repository = RepositoryFactory.get(PROJECT_REPOSITORY)
    return project_repository.get_all()
