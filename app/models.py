from .config import RepositoryFactory, EVENT_REPOSITORY, PROJECT_REPOSITORY


class AnalyticalEvent:

    def __init__(self, event_id, timestamp, event_type, uri, description, project_id):
        self.event_id = event_id
        self.uri = uri
        self.event_type = event_type
        self.description = description
        self.project_id = project_id
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.event_id}: {self.event_type} @ {self.timestamp}"


class Project:

    def __init__(self, project_id, project_name, project_description):
        self.project_id= project_id
        self.project_name = project_name
        self.project_description = project_description
        self._events = []

    def __repr__(self):
        return f"{self.project_id}: {self.project_name}"

    @property
    def events(self, timestamp):
        repository = RepositoryFactory.get(EVENT_REPOSITORY)
        return repository.get_all_for_project(project_id, timestamp)


    def create_event(self, event_type, uri, timestamp, description):
        repository = RepositoryFactory.get(EVENT_REPOSITORY)
        event_id = repository.get_new_id()
        event = AnalyticalEvent(event_id, timestamp, event_type, uri, description, self.project_id)
        repository.add(event)
        return event

    






