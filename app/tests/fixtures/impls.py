from ...repositories import AnalyticalEventRepository, ProjectRepository
from ...models import AnalyticalEvent, Project


class InmemoryAnalyticalRepository(AnalyticalEventRepository):

    def __init__(self, events):
        self.events = events

    def get_all_for_project(self, project_id, timestamp):
        return [u for u in self.events if u.project_id == project_id and u.timestamp <= timestamp] 

    def get_by_id(self, event_id):
        try:
            print('[*] Events', next((u for u in self.events if u.event_id == event_id )))
            return next((u for u in self.events if u.event_id == event_id ))
        except StopIteration:
            raise EventNotFound()

    def add(self, event):
        if not event.event_id:
            event.event = self.get_new_id()
        self.events.append(event)
        return event.event_id

    def get_new_id(self):
        return max(u.event_id for u in self.events) + 1

class InmemoryProjectRepository(ProjectRepository):

    def __init__(self, projects):
        self.projects = projects
    
    def get_by_id(self, project_id):
        try:
            return next((u for u in self.projects if u.project_id == project_id))
        except StopIteration:
            pass

    def get_all(self):
        return self.projects

    def get_new_id(self):
        return max(u.project_id for u in self.projects) + 1

    def upsert(self, project):
        if project.project_id:
            try:
                _project = next((u for u in self.projects if u.project_id == project.project_id ))
                for key in _project.__dict__:
                    _project.__dict__[key] = getattr(project, key, None)
                return _project
            except StopIteration:
                pass
        if not project.project_id:
            project.project_id = self.get_new_id()
        self.projects.append(project)
        return project.project_id
            

class ProjectNotFound(Exception):
    pass

class EventNotFound(Exception):
    pass
